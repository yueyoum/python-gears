from django.contrib import admin

from models import Notice, FriendLinks


class NoticeAdmin(admin.ModelAdmin):
    list_display = ('id', 'content', 'create_time',)


class FriendLinksAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'order_id', 'active',)
    def save_model(self, request, obj, form, change):
        if not obj.url.startswith('http://'):
            obj.url = 'http://%s' % obj.url
        obj.save()

admin.site.register(Notice, NoticeAdmin)
admin.site.register(FriendLinks, FriendLinksAdmin)