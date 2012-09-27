import json
import re
import hashlib
import time
import random


from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.core.paginator import Paginator
from django.core.urlresolvers import reverse
from django import template
from django.template import RequestContext
from django.utils.translation import ugettext as _
from django.core.mail import send_mail

from models import Member, Category, Node, Topic, Reply, Notify
from decorator import login_needed, post_needed, exception_handler
from exception import Http403
from service import Log
import appsettings
from webcache import (get_web_statistics,
                      get_notice,
                      get_friendlinks,
                      get_members_amount,
                      get_hot_members)


template.add_to_builtins('main.templatetags.customtags')

EMAIL_PATTERN = re.compile('.+@.+\..+')
POST_STRIP_PATTERN = re.compile('<.+?>|&nbsp;', re.M)
REPLY_TO_PATTERN = re.compile('<a.+?_reply_to="([^\s]+)">')


PAGE_RANGE = range(-2, 3)
PER_PAGE_TOPICS = appsettings.PER_PAGE_TOPICS




web_error_log = Log('web_error.log')
mail_log = Log('mail.log')



def token_generator(email):
    _token = '{0}{1}{2}'.format(
        email, random.randint(1, 10000), time.time()
    )
    return hashlib.sha1(_token).hexdigest()



def get_notify(member):
    if not member:
        return []
        
    notifies = member.notify.order_by('-create_time')
    
    def _parse(n):
        _res = {
            'id': n.id,
            'who': n.from_member_username,
            'at': n.get_target_info(),
            'noti_type': n.noti_type,
            'noti_chinese': appsettings.NOTI_TYPE_CHINESE[n.noti_type],
            'time': n.create_time,
        }
        return _res
    
    return [_parse(n) for n in notifies]


def add_notify(noti_type, member_obj, from_member_id, target_id=0):
    if member_obj.id == from_member_id:
        # can not give a notify to self
        return
    
    Notify.objects.create(
        member = member_obj,
        from_member_id = from_member_id,
        noti_type = noti_type,
        target_id = target_id
    )
    


@exception_handler
def _paging_maker(request, queryset, items_per_page):
    """
    A common paging for web page,
    If Http404 occurred, return a HttpResponse object with 404 status_code,
    else return a dict object which contents a sequence of paging info.
    """
    
    page = request.GET.get('p', '1')
    if not page.isdigit():
        raise Http404
    
    p = Paginator(queryset, items_per_page)
    
    page = int(page)
    if page < 1 or page > p.num_pages:
        raise Http404
    
    _render_page = [i + page for i in PAGE_RANGE if i + page > 0]
    if p.num_pages in _render_page:
        _render_page = _render_page[:_render_page.index(p.num_pages) + 1]
        
    if 1 not in _render_page:
        if _render_page[0] != 2:
            _render_page.insert(0, '...')
        _render_page.insert(0, 1)
        
    if p.num_pages not in _render_page:
        if _render_page[-1] + 1 != p.num_pages:
            _render_page.append('...')
        _render_page.append(p.num_pages)
        
    def _gen_page_sequence(x):
        return {
            'page': x,
            'disable': isinstance(x, str) or isinstance(x, unicode),
            'active': x == page,
            'link': '?p={0}'.format(x),
        }
        
    current_page = p.page(page)
    _result = {
        'pages': [_gen_page_sequence(i) for i in _render_page],
        'has_pre': current_page.has_previous(),
        'has_next': current_page.has_next(),
        'pre_link': '?p={0}'.format(current_page.previous_page_number()),
        'next_link': '?p={0}'.format(current_page.next_page_number()),
        'topics': current_page.object_list,
    }
        
    return _result
    



def register(request):
    username_value = ''
    email_value = ''
    form_msg = ''
    
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        password2 = request.POST.get('password2', '').strip()
        
        username_value = username
        email_value = email
        
        def _check_form():
            if not username:
                return _('need username')
            if Member.objects.filter(username=username).count() > 0:
                return _('username already exists')
            if not email or EMAIL_PATTERN.match(email) is None:
                return _('need email or email not valid')
            if Member.objects.filter(email=email).count() > 0:
                return _('email already exists')
            if not password or len(password) < 4:
                return _('need password, at least 4 character')
            if password != password2:
                return _('two password not same')
            return ''
        
        form_msg = _check_form()
        if not form_msg:
            try:
                Member.objects.create(
                    email = email,
                    username = username,
                    password = hashlib.sha1(password).hexdigest(),
                    token = token_generator(email),
                )
            except Exception, e:
                web_error_log.write(
                    'register create Member error. {0}'.format(repr(e))
                )
                form_msg = _('server error, try later')
            else:
                # success
                return HttpResponseRedirect(
                    '{0}?register=success'.format(reverse('login'))
                )
            
    return render_to_response(
        'account/registration.html',
        {
            'form_msg': form_msg,
            'username_value': username_value,
            'email_value': email_value
        },
        context_instance=RequestContext(request)
    )


def login(request):
    username_value = ''
    form_msg = ''
    already_logged = True if request.member else False
    
    from_register = request.GET.get('register', '')
    
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        autologin = request.POST.get('autologin')
        
        username_value = username
        
        def _login():
            if not username or not password:
                return _('need username and password')
            try:
                m = Member.objects.get(username=username)
            except Member.DoesNotExist:
                return _('username does not exist')
            if hashlib.sha1(password).hexdigest() != m.password:
                return _('wrong password')
            if not m.active:
                return _('user not active')
            
            request.session['member_token'] = m.token
            if autologin != u'on':
                request.session.set_expiry(0)
            return ''
        
        form_msg = _login()
        if not form_msg:
            # login success
            redirect_to = request.GET.get('next', '/')
            return HttpResponseRedirect(redirect_to)
    
        
    return render_to_response(
        'account/login.html',
        {
            'already_logged': already_logged,
            'username_value': username_value,
            'form_msg': form_msg,
            'from_register': from_register == 'success',
        },
        context_instance=RequestContext(request)
    )


def logout(request):
    try:
        del request.session['member_token']
    except:
        pass
    return HttpResponse('', mimetype='application/json')


def renew_password(request):
    _res = ''
    show_form = True
    success = True
    
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        
        def _check_email():
            if not email or EMAIL_PATTERN.match(email) is None:
                return _('need email or email not valid')
            try:
                _m = Member.objects.get(email=email)
            except:
                return _('this email not registered')
            return _m
        
        _res = _check_email()
        if isinstance(_res, Member):
            _url = '{0}{1}'.format(
                request.get_host(),
                reverse(
                    'changepassword',
                    kwargs={'username': _res.username, 'token': _res.token}
                )
            )
            
            _res = ''
            show_form = False
            _content = appsettings.EMAIL_CONTENT_RENEW_PASSWORD % _url
            try:
                mail_res = send_mail('New password', _content, '', [email])
            except Exception, e:
                mail_log.write(
                    'send mail to {0} error. {1}'.format(email, repr(e))
                )
                success = False
            else:
                if mail_res == 1:
                    success = True
                    mail_log.write(
                        'send mail to {0} success.'.format(email)
                    )
                else:
                    success = False
                    mail_log.write(
                        'send mail to {0} failure. return code = {1}'.format(
                            email, mail_res
                            )
                    )
            
            
    return render_to_response(
        'account/renew_password.html',
        {
            'show_form': show_form,
            'form_msg': _res,
            'success': success
        },
        context_instance = RequestContext(request)
    )


@exception_handler
def change_password(request, username, token):
    this_member = get_object_or_404(Member, username=username)
    if this_member.token != token:
        raise Http403
    
    if request.member and request.member.username != username:
        raise Http403
    
    changed = False
    email_value = ''
    form_msg = ''
    
    if request.method == 'POST':
        check_email = request.POST.get('check_email', '1')
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        
        def _check_form():
            if not password or len(password) < 4:
                return _('need password, at least 4 character')
            if check_email == '1':
                if not email or EMAIL_PATTERN.match(email) is None:
                    return _('need email or email not valid')
                if this_member.email != email:
                    return _('email not match')
            return ''
        
        form_msg = _check_form()
        if not form_msg:
            this_member.token = token_generator(this_member.email)
            this_member.password = hashlib.sha1(password).hexdigest()
            this_member.save()
            changed = True
                    
    return render_to_response(
        'account/change_password.html',
        {
            'changed': changed,
            'email_value': email_value,
            'form_msg': form_msg
        },
        context_instance = RequestContext(request)
    )



def index(request):
    """
    Web index page, display topics order by 'last_update' desc
    """
    
    topics = Topic.objects.order_by('-last_update')
    paging = _paging_maker(request, topics, PER_PAGE_TOPICS)
    if not isinstance(paging, dict):
        # if paging is not a instance of dict,
        # means, there are some exceptions occurred in _paging_maker function
        # and this exception had been catched by decorator 'exception_handler'
        # it returns a HttpResponse object.
        # so, just return paing.
        return paging
    
    
    paging.update(
        {
            'notify': get_notify(request.member),
            'notice': get_notice(),
            'statistics': get_web_statistics(),
            'friendlinks': get_friendlinks(),
        }
    )
    
    return render_to_response(
        'index.html',
        paging,
        context_instance = RequestContext(request)
    )
    
    
    
def members(request):
    members = Member.objects.filter(active=True)
    
    new_members = members.order_by('-regist_time').only('email', 'username')[:21]
    
    return render_to_response(
        'member/members.html',
        {
            'members_amount': get_members_amount(),
            'hot_members': get_hot_members(),
            'new_members': new_members,
        },
        context_instance = RequestContext(request)
    )

def _find_member_obj(func):
    def wrap(*args, **kwargs):
        member_obj = kwargs.get('member_obj', None)
        member_id = kwargs.get('member_id', None)
        if not member_obj and not member_id:
            raise Exception('need member')
            
        if member_id:
            member_obj = Member.objects.get(id=member_id)
            kwargs['member_obj'] = member_obj
            
        return func(*args, **kwargs)
    wrap.func_name = func.func_name
    wrap.__doc__ = wrap.__doc__
    return wrap


    
    
@_find_member_obj
def _is_self(self, member_obj=None, member_id=None):
    if not self:
        return False
    return self.id == member_obj.id

@_find_member_obj
def _has_following(self, member_obj=None, member_id=None):
    if not self:
        return False
    if _is_self(self, member_obj=member_obj, member_id=member_id):
        return False
    return self.has_following(target_obj=member_obj)
    

@exception_handler
def member_one(request, username):
    """
    member's personal page, showing some info about this member
    """
    
    m = get_object_or_404(Member, username=username)
    
    @_find_member_obj
    def _this_member_topic(member_obj=None, member_id=None, limit=10):
        return member_obj.topics.order_by('-last_update')[:limit]
        
        
    @_find_member_obj
    def _this_member_likes(member_obj=None, member_id=None, limit=10):
        return member_obj.topics_like.order_by('-last_update')[:limit]
        
        
    @_find_member_obj
    def _this_member_replied(member_obj=None, member_id=None, limit=10):
        _topic_ids = member_obj.replies.order_by(
            '-topic__last_update'
        ).values_list('topic__id', flat=True).distinct()
        
        replied_topics = Topic.objects.filter(
            id__in=_topic_ids
        ).order_by('-last_update')[:limit]
        
        return replied_topics
        
        
    return render_to_response(
        'member/member_one.html',
        {
            'this_member': m,
            'topics': _this_member_topic(member_obj=m),
            'topics_like': _this_member_likes(member_obj=m),
            'replied_topics': _this_member_replied(member_obj=m),
            'is_self': _is_self(self=request.member, member_obj=m),
        },
        context_instance = RequestContext(request)
    )
        
    
    
    

#@post_needed
#@login_needed(status=403)
#def follow(request):
#    '''
#    post via ajax.
#    param:
#    target_id: who to follow/unfollow
#    action: 1 => follow, 0 => unfollow
#    '''
#    target_id = request.POST.get('target_id', None)
#    action = request.POST.get('action', None)
#    if not target_id or not action:
#        msg = 'need param'
#    else:
#        try:
#            target_member = Member.objects.get(id=int(target_id))
#        except Member.DoesNotExist:
#            msg = 'target not found'
#        else:
#            if int(action) == 1:
#                request.member.add_following(target_obj=target_member)
#            else:
#                request.member.del_following(target_obj=target_member)
#            msg = 'ok'
#    return HttpResponse(json.dumps(msg), mimetype='application/json')



def nodes(request):
    def _gen_category_info(c):
        return {
            'name': c.name,
            'nodes': c.nodes.all()
        }
    
    categories = [_gen_category_info(c) for c in Category.objects.order_by('sign_id')]
    
    return render_to_response(
        'node/nodes.html',
        {
            'categories': categories,
        },
        context_instance = RequestContext(request)
    )
    

@exception_handler
def node_one(request, node_name):
    node = get_object_or_404(Node, name=node_name)
    topics = node.topics.order_by('-last_update')
    
    paging = _paging_maker(request, topics, PER_PAGE_TOPICS)
    if not isinstance(paging, dict):
        return paging
    
    has_joined = request.member and node.has_joined(request.member)
    paging.update({'node': node, 'has_joined': has_joined})
    
    return render_to_response(
        'node/node_one.html',
        paging,
        context_instance = RequestContext(request)
    )



@exception_handler
def topic(request, topic_id):
    """
    display topic which id == topic_id. and handle replies.
    """
    
    this_topic = get_object_or_404(Topic, id=int(topic_id))
    
    reply_msg = ''
    reply_value = ''
    if request.method == 'POST':
        content = request.POST.get('content', None)
        if not content:
            reply_msg = _('need content')
        else:
            reply_value = content
            _content = POST_STRIP_PATTERN.sub('', content)
            _content = _content.replace(' ', '')
            if len(_content) < 2:
                reply_msg = _('content need more than 2 characters')
            elif not request.member:
                reply_msg = _('need login')
            else:
                try:
                    Reply.objects.create(
                        topic = this_topic,
                        content = content,
                        replied_by = request.member
                    )
                except Exception, e:
                    web_error_log.write(
                        'create Reply error. {0}'.format(repr(e))
                    )
                    reply_msg = _('server error, try later')
                else:
                    # add reply notify
                    _reply_to = [this_topic.posted_by.username]
                    _reply_to.extend(REPLY_TO_PATTERN.findall(content))
                    _reply_to = set(_reply_to)
                    
                    for _r_name in _reply_to:
                        try:
                            _r_who = Member.objects.get(username=_r_name)
                        except:
                            continue
                        else:
                            add_notify(
                                noti_type = appsettings.NOTI_TYPE['reply'],
                                member_obj = _r_who,
                                from_member_id = request.member.id,
                                target_id = this_topic.id
                            )
                    
                    return HttpResponseRedirect(
                        '{0}#last_reply'.format(
                            reverse('viewtopic', kwargs={'topic_id': topic_id})
                        )
                    )
        
    
    this_member_topics = this_topic.posted_by.topics.only('id', 'title')[:10]
    return render_to_response(
        'topic/topic.html',
        {
            'topic': this_topic,
            'replies': this_topic.replies.order_by('reply_time'),
            'reply_msg': reply_msg,
            'this_member_topics': this_member_topics,
            'reply_value': reply_value,
            'editable': request.member and request.member == this_topic.posted_by,
            'already_like': request.member and this_topic.has_liked(request.member)
        },
        context_instance = RequestContext(request)
    )
    

@login_needed(status=302)
def topic_new(request):
    """
    post new topic,
    if post success, redirect to the topic view page.
    else display the error msg. keep the user input.
    """
    
    node_value = ''
    title_value = ''
    content_value = ''
    form_msg = ''
    
    if request.method == 'POST':
        node = request.POST.get('node', '').strip()
        title = request.POST.get('title', '').strip()
        content = request.POST.get('content', '').strip()
        topic_id = request.POST.get('topic_id', '')
        
        if not topic_id.isdigit():
            topic_id = 0
        else:
            topic_id = int(topic_id)
            
        # topic_id == 0, means this is a new post
        # or, a existed topic that have been modified.
        
        node_value = node
        title_value = title
        content_value = content
        
        def check_form():
            if not node:
                return _('need node')
            try:
                Node.objects.get(name=node)
            except:
                return _('node does not exists')
            if not title:
                return _('need title')
            if len(title) > 100:
                return _('title length should less than 100 characters')
            if not content:
                return _('need content')
            _content = POST_STRIP_PATTERN.sub('', content)
            if len(_content) < 2:
                return _('content need more than 2 characters')
            return ''
        
        form_msg = check_form()
        if not form_msg:
            # everything is ok, create or update Topic
            if topic_id:
                # modify a exist topic
                _exist_topic = Topic.objects.get(id=topic_id)
                if _exist_topic.node.name != node:
                    _exist_topic.node = Node.objects.get(name=node)
                if _exist_topic.title != title:
                    _exist_topic.title = title
                if _exist_topic.content != content:
                    _exist_topic.content = content
                _exist_topic.save()
                return HttpResponseRedirect(
                    reverse('viewtopic', kwargs={'topic_id': topic_id})
                )
            else:
                try:
                    new_topic = Topic.objects.create(
                        node = Node.objects.get(name=node),
                        title = title,
                        content = content,
                        posted_by = request.member
                    )
                except Exception, e:
                    web_error_log.write('create Topic error. {0}'.format(repr(e)))
                    form_msg = _('server error, try later')
                else:
                    return HttpResponseRedirect(
                        reverse('viewtopic', kwargs={'topic_id': new_topic.id})
                    )
    
    # render out this web page
    
    _choose_node_name = request.GET.get('node', '')
    if _choose_node_name:
        node_value = _choose_node_name
        
    def _node_list(n):
        return {
            'name': n.name,
            'selected': node_value == n.name
        }
    
    return render_to_response(
        'topic/topic_new.html',
        {
            'form_msg': form_msg,
            'nodes': [_node_list(n) for n in Node.objects.all()],
            'title_value': title_value,
            'content_value': content_value,
        },
        context_instance=RequestContext(request),
    )


@exception_handler
@login_needed(status=302)
def topic_edit(request, topic_id):
    topic = get_object_or_404(Topic, id=int(topic_id))
        
    if topic.posted_by.id != request.member.id:
        raise Http403
        
    def _node_list(n):
        return {
            'name': n.name,
            'selected': n.name == topic.node.name
        }
        
    return render_to_response(
        'topic/topic_new.html',
        {
            'topic_id': topic.id,
            'title_value': topic.title,
            'content_value': topic.content,
            'nodes': [_node_list(n) for n in Node.objects.all()],
            'post_to': reverse('newpost'),
        },
        context_instance = RequestContext(request)
    )

    
    
@login_needed(status=302)
def my_concern(request):
    """Only show the topics which are belongs to my joined nodes"""
    
    node_ids = request.member.nodes.values_list('id', flat=True)
    
    topics = Topic.objects.filter(node__id__in=node_ids).order_by('-last_update')
    paging = _paging_maker(request, topics, PER_PAGE_TOPICS)
    if not isinstance(paging, dict):
        return paging
    
    return render_to_response(
        'display_topics.html',
        paging,
        context_instance = RequestContext(request)
    )



@exception_handler
def member_posts(request, username):
    """show topics which are posted by username"""
    
    this_member = get_object_or_404(Member, username=username)
        
    topics = this_member.topics.order_by('-last_update')
    paging = _paging_maker(request, topics, PER_PAGE_TOPICS)
    if not isinstance(paging, dict):
        return paging
    
    paging.update({
        'editable': request.member and request.member.username == username,
    })
        
    return render_to_response(
        'display_topics.html',
        paging,
        context_instance = RequestContext(request)
    )



@exception_handler
def member_replies(request, username):
    """show topics which are replied by username"""
    
    this_member = get_object_or_404(Member, username=username)
    
    topic_ids = this_member.replies.order_by(
        'topic__id').values_list('topic__id', flat=True).distinct()
    
    topics = Topic.objects.filter(id__in=topic_ids).order_by('-last_update')
    paging = _paging_maker(request, topics, PER_PAGE_TOPICS)
    if not isinstance(paging, dict):
        return paging

    return render_to_response(
        'display_topics.html',
        paging,
        context_instance = RequestContext(request)
    )


@exception_handler
def member_likes(request, username):
    """show topics which are liked by username"""
    
    this_member = get_object_or_404(Member, username=username)
    
    topics = this_member.topics_like.order_by('-last_update')
    paging = _paging_maker(request, topics, PER_PAGE_TOPICS)
    if not isinstance(paging, dict):
        return paging

    return render_to_response(
        'display_topics.html',
        paging,
        context_instance = RequestContext(request)
    )


@post_needed
@login_needed(status=403)
def member_node_ajax(request):
    """
    Member join/quit a Node. action: 1 => join, 0 => quit. Ajax POST
    """
    
    _res_code = '2'
    
    node_name = request.POST.get('node_name', '')
    action = request.POST.get('action', '')
    
    if node_name and action:
        try:
            node = Node.objects.get(name=node_name)
        except Exception, e:
            web_error_log.write('member_node, get Node error. {0}'.format(repr(e)))
        else:
            if action == '1':
                node.add_member(request.member)
                _res_code = '0'
            if action == '0':
                node.del_member(request.member)
                _res_code = '1'
        
    return HttpResponse(json.dumps(_res_code), mimetype='application/json')
    
    
    
@post_needed
@login_needed(status=403)
def member_topic_ajax(request):
    """
    Member like/unlike a Topic, action: 1 => like, 0 => unlike. Ajax POST
    """
    
    _res_code = '2'
    
    topic_id = request.POST.get('topic_id', '')
    action = request.POST.get('action', '')
    
    if topic_id and topic_id.isdigit() and action:
        try:
            topic = Topic.objects.get(id=int(topic_id))
        except Exception, e:
            web_error_log.write('member_topic, get Topic error. {0}'.format(repr(e)))
        else:
            _noti_type = 0
            if action == '1':
                _success = topic.add_like(request.member)
                _res_code = '0'
                
                if _success:
                    _noti_type = appsettings.NOTI_TYPE['like']
                    
            elif action == '0':
                topic.remove_like(request.member)
                _res_code = '1'
                _noti_type = appsettings.NOTI_TYPE['unlike']
                
            # send notify
            if _noti_type:
                add_notify(
                    noti_type = _noti_type,
                    member_obj = topic.posted_by,
                    from_member_id = request.member.id,
                    target_id = topic.id
                )
                
                
    return HttpResponse(json.dumps(_res_code), mimetype='application/json')


@post_needed
@login_needed(status=403)
def member_notify_ajax(request):
    _res_code = '0'
    notify_id = request.POST.get('notify_id', '')
    
    if notify_id and notify_id.isdigit():
        try:
            n = Notify.objects.get(id=int(notify_id))
        except Exception, e:
            #web_error_log.write(
            #    'member_notify, get Notify id {0} error. {1}'.format(notify_id, repr(e))
            #)
            pass
        else:
            n.delete()
            _res_code = notify_id
            
    return HttpResponse(json.dumps(_res_code), mimetype='application/json')
