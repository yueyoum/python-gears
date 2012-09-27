# -*- coding: utf-8 -*-
import hashlib

from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter
@stringfilter
def truncatechinese(value, arg=13):
    if len(value) < arg+1:
        return value
    
    return '%s...' % value[:arg]
    
    
    
@register.filter
@stringfilter
def emptydescription(value, arg=u'木有签名'):
    return value if value else arg


@register.filter
@stringfilter
def to_md5(value):
    return hashlib.md5(value).hexdigest()