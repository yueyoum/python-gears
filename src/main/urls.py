from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('main.views',
    
    # index, home page
    url(r'^/?$', 'index', name='index'),
    
    # register, login, logout, change password
    url(r'^account/register/?$', 'register', name='register'),
    url(r'^account/login/$', 'login', name='login'),
    url(r'^account/logout/$', 'logout', name='logout'),
    url(r'^account/renewpassword/$', 'renew_password', name='renewpassword'),
    url(r'^account/changepassword/(?P<username>[^/]+)/(?P<token>[0-9a-f]{40})/?$',
        'change_password', name='changepassword'),
    
    
    # member
    url(r'^members/?$', 'members', name='members'),
    url(r'^member/(?P<username>[^/]+)/?$', 'member_one', name='viewmember'),
    url(r'^member/(?P<username>[^/]+)/posts/?$', 'member_posts', name='memberposts'),
    url(r'^member/(?P<username>[^/]+)/replies/?$', 'member_replies', name='memberreplies'),
    url(r'^member/(?P<username>[^/]+)/likes/?$', 'member_likes', name='memberlikes'),
    
    
    # join node, or like topics, ajax post
    url(r'^member-node/$', 'member_node_ajax'),
    url(r'^member-topic/$', 'member_topic_ajax'),
    url(r'^member-notify/$', 'member_notify_ajax'),
    
    
    # node
    url(r'^nodes/?$', 'nodes', name='nodes'),
    url(r'^node/(?P<node_name>[^/]+)/?$', 'node_one', name='viewnode'),
    
    
    
    # topic
    url(r'^topic/new/?$', 'topic_new', name='newpost'),
    url(r'^topic/(?P<topic_id>\d+)/?$', 'topic', name='viewtopic'),
    url(r'^topic/(?P<topic_id>\d+)/edit/?$', 'topic_edit', name='topicedit'),
    
    # personal stuff
    url(r'^my/concern/?$', 'my_concern', name='myconcern'),
)
