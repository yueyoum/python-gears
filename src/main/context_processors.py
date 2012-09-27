"""
add the following two line in TEMPLATE_CONTEXT_PROCESSORS in settings_base
    'main.context_processors.sitecontext',
    'main.context_processors.cached',
    
then, 'member', 'login_next' ... will be always render to template
"""



from appsettings import AVATAR_URL

from webcache import (get_important_topics,
                      get_hot_topics,
                      get_welcomed_topics,
                      get_node_items)



def sitecontext(request):
    return {
        'member': request.member,
        'login_next': '/' if request.path.startswith('/account/') else request.path,
        'avatar_url': AVATAR_URL,
    }
    
    
    
def cached(request):
    return {
        'important_topics': get_important_topics(),
        'hot_topics': get_hot_topics(),
        'welcomed_topics': get_welcomed_topics(),
        'node_items': get_node_items(),
    }