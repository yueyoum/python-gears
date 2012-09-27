from django.shortcuts import get_object_or_404
from django.db.models import F

from models import Member, Topic
from decorator import exception_handler


class MemberAuth(object):
    def process_request(self, request):
        member_obj = None
        _token = request.session.get('member_token', None)
        if _token:
            try:
                member_obj = Member.objects.get(token=_token)
                if not member_obj.active:
                    member_obj = None
            except:
                pass
        setattr(request, 'member', member_obj)
        return None
    
    
class IncreaseTopicViewAmount(object):
    @exception_handler
    def process_view(self, request, view_func, args, kwargs):
        if view_func.func_name == 'topic':
            t = get_object_or_404(Topic, id=int(kwargs['topic_id']))
            t.views_amount = F('views_amount') + 1
            t.save()
        return None
