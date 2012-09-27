from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.handlers.wsgi import WSGIRequest

from exception import Http403
from service import Log


def login_needed(**params):
    '''
    params:
    status: [302, 403, 404...],  required
    redirect_to: if status is 302, where to redirect, not required
    '''
    
    status = params.get('status', None)
    if not status:
        raise ValueError('login_needed need a status param')
        
    def deco(func):
        def wrap(request, *args, **kwargs):
            if request.member:
                return func(request, *args, **kwargs)
                
            if status != 302:
                return HttpResponse(status=status)
            
            redirect_to = params.get('redirect_to', None)
            if not redirect_to:
                redirect_to = '{0}?next={1}'.format(
                    reverse('login'), request.path
                )
            return HttpResponseRedirect(redirect_to)
        
        wrap.func_name = func.func_name
        wrap.__doc__ = func.__doc__
        return wrap
    return deco


def post_needed(func):
    def wrap(request, *args, **kwargs):
        if request.method != 'POST':
            return HttpResponse(status=403)
            
        return func(request, *args, **kwargs)
        
    wrap.func_name = func.func_name
    wrap.__doc__ = func.__doc__
    return wrap


#def mute_error(*params):
#    '''
#    params: 404 or 500, not required.
#    if not specified, default is 404.
#    '''
#    
#    if len(params) < 1:
#        status = 404
#    else:
#        status = params[0]
#        if status not in [404, 500]:
#            raise Exception('status must be 404 or 500')
#            
#    def deco(func):
#        def wrap(*args, **kwargs):
#            try:
#                _res = func(*args, **kwargs)
#            except Exception, e:
#                # TODO: log error here
#                # 404 or 500 handler
#                _res = HttpResponse('')
#            return _res
#        wrap.func_name = func.func_name
#        wrap.__doc__ = func.__doc__
#        return wrap
#    return deco


log_404_403 = Log('404_403.log')

def exception_handler(func):
    """
    view func maybe raise Http404 or Http403,
    catch this exception and return a 404/403 page
    """
    
    def wrap(*args, **kwargs):
        _request = None
        for a in args:
            if isinstance(a, WSGIRequest):
                _request = a
                break
            
        def _response(template_name):
            if _request:
                _res = render_to_response(
                    template_name, {}, context_instance = RequestContext(_request)
                )
            else:
                _res = render_to_response(template_name)
            return _res
            
        try:
            _res = func(*args, **kwargs)
        except Http404:
            log_404_403.write(
                '404, {0}, {1}'.format(
                    _request.member.username if _request else 'Anonymous',
                    func.func_name,
                )
            )
            
            _res = _response('404.html')
            _res.status_code = 404
        except Http403:
            log_404_403.write(
                '403, {0}, {1}'.format(
                    _request.member.username if _request else 'Anonymous',
                    func.func_name,
                )
            )
            
            _res = _response('403.html')
            _res.status_code = 403
        return _res
    wrap.func_name = func.func_name
    wrap.__doc__ = func.__doc__
    return wrap


