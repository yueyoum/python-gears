from django.contrib import admin
from django import forms

from models import RelationShip, Member, Category, Node, Topic, Reply, Notify


#class RelationShipAdmin(admin.ModelAdmin):
#    list_display = (
#        'id',
#        'followed',
#        'following',
#        'follow_time',
#    )
#    
#    list_filter = ('followed', 'following', )
#    ordering = ('-follow_time',)
#    
#    def has_add_permission(self, request):
#        return False
#    
#    def has_delete_permission(self, request, obj=None):
#        return False
#    
#    def has_change_permission(self, request, obj=None):
#        return False
    
    

class MemberAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'email',
        'username',
        'post_amount',
        'likes_amount',
        'honor',
        #'Following',
        #'Followed_by',
        'active',
    )
    list_filter = ('active',)
    search_fields = ('username',)
    ordering = ('-honor',)
    
    #def Following(self, obj):
    #    _members = [i.username for i in obj.following]
    #    return '<br/>'.join(_members)
    #Following.allow_tags = True
    #
    #def Followed_by(self, obj):
    #    _members = [i.username for i in obj.followed_by]
    #    return '<br/>'.join(_members)
    #Followed_by.allow_tags = True
    
    def has_add_permission(self, request):
        return False
    

class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'nodes',
    )
    
    def nodes(self, obj):
        _nodes = obj.nodes.values_list('name', flat=True)
        return ', '.join(_nodes)



class NodeAdminForm(forms.ModelForm):
    class Meta:
        model = Node
        
    def clean(self):
        cleaned_data = self.cleaned_data
        name = cleaned_data.get('name')
        if ' ' in name:
            raise forms.ValidationError(u'node name can not contains blank')
        return cleaned_data


class NodeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'category',
        'description',
        'member_amount',
        'topic_amount',
    )
    ordering = ('-topic_amount',)
    list_filter = ('category',)
    
    fieldsets = (
        (None, {
            'fields': ('category', 'name', 'description',)
        }),
    )
    
    form = NodeAdminForm
    

class ReplyInline(admin.TabularInline):
    model = Reply
    extra = 0


class TopicAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'node',
        'title',
        'posted_by',
        'views_amount',
        'reply_amount',
        'likes_amount',
        'last_update',
        'important',
    )
    list_filter = ('important', 'node', 'posted_by',)
    search_fields = ('title',)
    ordering = ('-last_update',)
    inlines = [ReplyInline,]
    
    fieldsets = (
        (None, {
            'fields': ('node', 'title', 'content', 'important',)
        }),
    )
    
    def has_add_permission(self, request):
        return False
    

#class ReplyAdmin(admin.ModelAdmin):
#    list_display = (
#        'id',
#        'topic',
#        'replied_by',
#        'reply_time'
#    )
#    
#    list_filter = ('topic', 'replied_by',)
#    ordering = ('-reply_time',)
    
    #def has_add_permission(self, request):
    #    return False
    
    
    
class NotifyAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'From',
        'To',
        'Topic',
        'create_time',
    )
    
    ordering = ('-create_time',)
    
    def From(self, obj):
        return obj.from_member_username
    
    def To(self, obj):
        return obj.member.username
    
    def Topic(self, obj):
        _t = obj.get_target_info()
        if _t is None:
            return ''
        return _t.title
    
    
    def has_add_permission(self, request):
        return False
    
    
    
    
admin.site.register(Topic, TopicAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Node, NodeAdmin)
admin.site.register(Member, MemberAdmin)
#admin.site.register(RelationShip, RelationShipAdmin)
#admin.site.register(Reply, ReplyAdmin)
admin.site.register(Notify, NotifyAdmin)