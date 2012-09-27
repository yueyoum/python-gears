import datetime

from django.db import models
from django.db.models import F


INC_POST = 3
INC_POST_REPLY = 1
INC_LIKE = 1
INC_FOLLOW = 2


# follow not used
# but keep the code of 'follow'


class RelationShip(models.Model):
    followed = models.ForeignKey('Member', related_name='following_member')
    following = models.ForeignKey('Member', related_name='followed_member')
    follow_time = models.DateTimeField(auto_now_add=True)



class Member(models.Model):
    """
    >>> one = Member.objects.create(email='a@a.com',\
    username='one', password='1234')
    >>> two = Member.objects.create(email='b@b.com',\
    username='two', password='1234')
    >>> one.has_following(target_id=two.id)
    False
    >>> one.add_following(target_obj=two)
    >>> one.has_following(target_id=two.id)
    True
    >>> Member.objects.get(username='two').honor
    2
    >>> one.following_amount
    1
    >>> one.followed_by_amount
    0
    >>> two.following_amount
    0
    >>> two.followed_by_amount
    1
    >>> one.del_following(target_obj=two)
    >>> one.has_following(target_id=two.id)
    False
    >>> one.following_amount
    0
    >>> two.followed_by_amount
    0
    >>> Member.objects.get(username='two').honor
    0
    """
    
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=16, unique=True)
    password = models.CharField(max_length=40)
    active = models.BooleanField(default=True)
    regist_time = models.DateTimeField(auto_now_add=True)
    token = models.CharField(max_length=40, db_index=True)
    
    post_amount = models.IntegerField(default=0)
    likes_amount = models.IntegerField(default=0)
    honor = models.IntegerField(default=0)
    
    
    
    @property
    def following(self):
        return [i.following for i in self.following_member.order_by('-follow_time')]
    
    @property
    def followed_by(self):
        return [i.followed for i in self.followed_member.order_by('-follow_time')]
        
    @property
    def following_amount(self):
        return self.following_member.count()
        
    @property
    def followed_by_amount(self):
        return self.followed_member.count()
        
    
    def _find_target_obj(func):
        def wrap(*args, **kwargs):
            target_obj = kwargs.get('target_obj', None)
            target_id = kwargs.get('target_id', None)
            if not target_id and not target_obj:
                raise Exception('need target')
            if target_id:
                #self can not follow self
                if args[0].id == target_id:
                    return False
                
                target_obj = Member.objects.get(id=target_id)
                kwargs['target_id'] = None
                kwargs['target_obj'] = target_obj
                
            if args[0].id == kwargs['target_obj'].id:
                return False
            return func(*args, **kwargs)
        
        wrap.func_name = func.func_name
        wrap.__doc__ = func.__doc__
        return wrap
    
        
    @_find_target_obj
    def has_following(self, target_obj=None, target_id=None):
        return self.following_member.filter(following=target_obj).count() > 0
    
    @_find_target_obj
    def add_following(self, target_obj=None, target_id=None):
        if not self.has_following(target_obj=target_obj, target_id=target_id):
            self.following_member.create(following=target_obj)
            target_obj.honor = F('honor') + INC_FOLLOW
            target_obj.save()
            
    @_find_target_obj
    def del_following(self, target_obj=None, target_id=None):
        for i in self.following_member.filter(following=target_obj):
            i.delete()
            if target_obj.honor > INC_FOLLOW:
                target_obj.honor = F('honor') - INC_FOLLOW
                target_obj.save()
        
    
    @property
    def likes(self):
        return self.topics_like.order_by('-last_update').only('id', 'title')
        
    
    @property
    def notifies_amount(self):
        return self.notify.count()
        
        
        
    def __unicode__(self):
        return self.username
    
    
    class Meta:
        ordering = ['-honor']
        
        
        
###############################################
    
    
class Notify(models.Model):
    # noti_type is defined in appsettings
    
    member = models.ForeignKey(Member, related_name='notify')
    from_member_id = models.IntegerField()
    noti_type = models.SmallIntegerField()
    target_id = models.IntegerField(db_index=True)
    create_time = models.DateTimeField(auto_now_add=True)
    
    
    @property
    def from_member_username(self):
        return Member.objects.get(id=self.from_member_id).username
        
    def get_target_info(self):
        if self.target_id == 0:
            return None
        return Topic.objects.get(id=self.target_id)

    class Meta:
        ordering = ['create_time']


################################################


class Category(models.Model):
    name = models.CharField(max_length=16, unique=True)
    sign_id = models.PositiveSmallIntegerField(unique=True)
    
    def __unicode__(self):
        return self.name
    
    class Meta:
        ordering = ['sign_id']


class Node(models.Model):
    category = models.ForeignKey(Category, related_name='nodes')
    name = models.CharField(max_length=16, unique=True)
    description = models.CharField(max_length=255)
    members =  models.ManyToManyField(Member, related_name='nodes', null=True)
    topic_amount = models.IntegerField(default=0)
    member_amount = models.IntegerField(default=0)
    
    
    def has_joined(self, member_obj):
        if not member_obj:
            return False
        return self.members.filter(id=member_obj.id).count() > 0
    
    def add_member(self, member_obj):
        if self.has_joined(member_obj):
            return
        
        self.members.add(member_obj)
        
        # increase member_amount,
        # to avoid effect of F in multi-save, we use a tmp obj
        _self = Node.objects.get(id=self.id)
        _self.member_amount = F('member_amount') + 1
        _self.save()
        
        
    def del_member(self, member_obj):
        self.members.remove(member_obj)
        
        if self.member_amount > 0:
            _self = Node.objects.get(id=self.id)
            _self.member_amount = F('member_amount') - 1
            _self.save()
        
        
    def __unicode__(self):
        return self.name
    
    class Meta:
        ordering = ['-topic_amount']





class Topic(models.Model):
    node = models.ForeignKey(Node, related_name='topics')
    title = models.CharField(max_length=100, db_index=True)
    content = models.TextField()
    posted_by = models.ForeignKey(Member, related_name='topics')
    post_time = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now_add=True)
    
    views_amount = models.IntegerField(default=0)
    reply_amount = models.IntegerField(default=0)
    likes_amount = models.IntegerField(default=0)
    
    important = models.BooleanField(default=False)
    
    member_likes = models.ManyToManyField(
        Member, related_name='topics_like', null=True, blank=True
    )
    
    
    @property
    def has_reply(self):
        return self.reply_amount > 0
    
    @property
    def last_reply_member(self):
        return self.replies.order_by('-reply_time')[0].replied_by
        
    @property
    def last_reply_time(self):
        return self.replies.order_by('-reply_time')[0].reply_time
    
    @property
    def who_like(self):
        return self.member_likes.order_by('-honor').only('email', 'username')
    
    def has_liked(self, member_obj):
        if not member_obj:
            return False
        return self.member_likes.filter(id=member_obj.id).count() > 0
    
    def add_like(self, member_obj):
        if self.posted_by.id == member_obj.id:
            # can not like your own posts
            # wang po mai gua, zi mai zi kua
            return False
        if self.has_liked(member_obj):
            # this member has already like this topic
            return False
        self.member_likes.add(member_obj)
        
        _self = Topic.objects.get(id=self.id)
        _self.likes_amount = F('likes_amount') + 1
        _self.save()
        
        _m = Member.objects.get(id=self.posted_by.id)
        _m.honor = F('honor') + INC_LIKE
        _m.save()
        
        _member_obj = Member.objects.get(id=member_obj.id)
        _member_obj.likes_amount = F('likes_amount') + 1
        _member_obj.save()
        
        return True
    
    
    def remove_like(self, member_obj):
        member_obj = Member.objects.get(id=member_obj.id)
        self.member_likes.remove(member_obj)
        
        if self.likes_amount > 0:
            _self = Topic.objects.get(id=self.id)
            _self.likes_amount = F('likes_amount') - 1
            _self.save()
        
        if self.posted_by.honor >= INC_LIKE:
            _m = Member.objects.get(id=self.posted_by.id)
            _m.honor = F('honor') - INC_LIKE
            _m.save()
            
        if member_obj.likes_amount > 0:
            _member_obj = Member.objects.get(id=member_obj.id)
            _member_obj.likes_amount = F('likes_amount') - 1
            _member_obj.save()
        
    
    def __unicode__(self):
        return self.title[:20]
        
    class Meta:
        ordering = ['-last_update']
        
        
def _add_topic(sender, instance, created, **kwargs):
    if created:
        # F will be always work when save multi-times.
        # we don't wanna this
        # so, use a new object instead of `instance.xxx`
        _m = Member.objects.get(id=instance.posted_by.id)
        _m.post_amount = F('post_amount') + 1
        _m.honor = F('honor') + INC_POST
        _m.save()
        
        _n = Node.objects.get(id=instance.node.id)
        _n.topic_amount = F('topic_amount') + 1
        _n.save()
        
    
        
def _del_topic(sender, instance, **kwargs):
    _m = Member.objects.get(id=instance.posted_by.id)
    _n = Node.objects.get(id=instance.node.id)
    
    if _m.post_amount > 0:
        _m.post_amount = F('post_amount') - 1
    if _m.honor >= INC_POST:
        _m.honor = F('honor') - INC_POST
    _m.save()
    
    if _n.topic_amount > 0:
        _n.topic_amount = F('topic_amount') - 1
        _n.save()
        
        
models.signals.post_save.connect(receiver=_add_topic,
                                 sender=Topic,
                                 dispatch_uid='added_a_new_topic')

models.signals.post_delete.connect(receiver=_del_topic,
                                   sender=Topic,
                                   dispatch_uid='deleted_a_topic')
        
        
    
class Reply(models.Model):
    """
    >>> def get_one():\
        return Member.objects.get(username='one')
    >>> def get_two():\
        return Member.objects.get(username='two')
    
    >>> node = Node.objects.create(name='test_node', description='xxx')
    >>> def get_node():\
        return Node.objects.get(name='test_node')
    
    >>> topic = Topic.objects.create(node=node,\
                title='test_topic', content='zzz', posted_by=get_one())
    >>> def get_topic():\
        return Topic.objects.get(title='test_topic')
    
    >>> reply1 = Reply.objects.create(topic=topic,\
                content='reply_content', replied_by=get_one())
    
    >>> get_one().honor
    3
    >>> get_one().post_amount
    1
    >>> get_node().topic_amount
    1
    >>> get_topic().reply_amount
    1
    >>> get_topic().last_reply_member.username
    u'one'
    
    >>> import time
    >>> time.sleep(1)
    >>> reply2 = Reply.objects.create(topic=topic,\
                content='two_reply', replied_by=get_two())
    
    >>> get_two().honor
    1
    >>> get_topic().reply_amount
    2
    >>> get_topic().last_reply_member.username
    u'two'
    
    >>> reply2.delete()
    >>> get_topic().replies.count()
    1
    >>> get_topic().last_reply_member.username
    u'one'
    >>> get_two().honor
    0
    
    >>> get_topic().delete()
    >>> get_one().post_amount
    0
    >>> get_one().honor
    0
    >>> get_node().topic_amount
    0
    >>> Reply.objects.count()
    0
    """
    
    topic = models.ForeignKey(Topic, related_name='replies')
    content = models.TextField()
    replied_by = models.ForeignKey(Member, related_name='replies')
    reply_time = models.DateTimeField(auto_now_add=True)
    
    def __unicode__(self):
        return u'%s: %s' % (self.replied_by.username, self.content[:10])
    
    class Meta:
        ordering = ['-reply_time']
        verbose_name = 'Reply'
        verbose_name_plural = 'Replies'
        
        
def _add_reply(sender, instance, created, **kwargs):
    if created:
        _m = Member.objects.get(id=instance.replied_by.id)
        _t = Topic.objects.get(id=instance.topic.id)
        
        _m.honor = F('honor') + INC_POST_REPLY
        _m.save()
        
        _t.reply_amount = F('reply_amount') + 1
        _t.last_update = datetime.datetime.now()
        _t.save()
        

def _del_reply(sender, instance, **kwargs):
    _m = Member.objects.get(id=instance.replied_by.id)
    if _m.honor >= INC_POST_REPLY:
        _m.honor = F('honor') - INC_POST_REPLY
        _m.save()
        
    try:
        _t = Topic.objects.get(id=instance.topic.id)
    except:
        pass
    else:
        if _t.reply_amount > 0:
            _t.reply_amount = F('reply_amount') - 1
            _t.save()
    
    
    
models.signals.post_save.connect(receiver=_add_reply,
                                 sender=Reply,
                                 dispatch_uid='added_a_new_reply')

models.signals.post_delete.connect(receiver=_del_reply,
                                   sender=Reply,
                                   dispatch_uid='deleted_a_reply')
