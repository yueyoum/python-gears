"""
we use memcached to cache some db data.
function that been decorated by _cache(TIME),
this function will be cached.
"""


import os
import sys

from models import Topic, Node, Member, Reply
from service import MemcacheClient
from appsettings import CACHE_TIME 

current_path = os.path.dirname(os.path.realpath(__file__))
src_path = os.path.normpath(os.path.join(current_path, '..'))
sys.path.append(src_path)

from config.models import Notice, FriendLinks


mc = MemcacheClient()


def _cache(time):
    if not isinstance(time, int):
        raise Exception('Need Integer')
        
    def deco(func):
        def wrap(*args, **kwargs):
            _res = mc.get(func.func_name)
            if _res is None :
                _res = func(*args, **kwargs)
                mc.set(func.func_name, _res, time=time)
            return _res
        wrap.func_name = func.func_name
        return wrap
    return deco
            

@_cache(CACHE_TIME.get('members_amount', 60))
def get_members_amount():
    return Member.objects.count()


@_cache(CACHE_TIME.get('hot_members', 60))
def get_hot_members(limit=21):
    return Member.objects.filter(active=True).order_by('-honor').only(
        'email', 'username'
    )[:limit]


@_cache(CACHE_TIME.get('important_topics', 60))
def get_important_topics(limit=4):
    return Topic.objects.filter(important=True).order_by('-last_update')[:limit]

@_cache(CACHE_TIME.get('hot_topics', 60))
def get_hot_topics(limit=8):
    return Topic.objects.order_by('-reply_amount')[:limit]
    
@_cache(CACHE_TIME.get('welcomed_topics', 60))
def get_welcomed_topics(limit=8):
    return Topic.objects.order_by('-likes_amount')[:limit]
    
    
    
@_cache(CACHE_TIME.get('web_statistics', 60))
def get_web_statistics():
    return {
        'nodes': Node.objects.count(),
        'members': Member.objects.count(),
        'topics': Topic.objects.count(),
        'replies': Reply.objects.count(),
    }
    
    
@_cache(CACHE_TIME.get('notice', 60))
def get_notice():
    if Notice.objects.count() == 0:
        return ''
    return Notice.objects.order_by('-create_time')[0].content
    
    
@_cache(CACHE_TIME.get('friendlinks', 60))
def get_friendlinks():
    return FriendLinks.objects.filter(active=True).order_by('order_id')
    
    
    
@_cache(CACHE_TIME.get('node_items', 60))
def get_node_items():
    return Node.objects.order_by('-topic_amount').only('name', 'topic_amount')
