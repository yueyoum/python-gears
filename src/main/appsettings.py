# -*- coding: utf-8 -*-

AVATAR_URL = {
    'prefix': 'http://avatar.ofeva.com/avatar/',
    'default': '',
}

NOTI_TYPE = {
    'reply': 1,
    'like': 2,
    'unlike': 3,
    'follow': 4,
    'unfollow': 5,
}

NOTI_TYPE_CHINESE = {
    1: '回复了你',
    2: '喜欢',
    3: '不再喜欢',
    4: '成为了你的粉丝',
    5: '不再是你的粉丝了',
}

PER_PAGE_TOPICS = 18

EMAIL_CONTENT_RENEW_PASSWORD = """
复制下面的链接，用浏览器打开，按照提示操作，即可完成重置密码。

%s
"""


CACHE_TIME = {
    'important_topics': 5 * 60,
    'hot_topics': 3 * 60,
    'welcomed_topics': 3 * 60,
    'web_statistics': 3 * 60,
    'notice': 5 * 60,
    'friendlinks': 5 * 60,
    'hot_members': 5 * 60,
    'members_amount': 3 * 60,
    'node_items': 3 * 60,
} 
