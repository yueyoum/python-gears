from django.db import models

# Create your models here.

class Notice(models.Model):
    content = models.TextField()
    create_time = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-create_time']
        
        
        
class FriendLinks(models.Model):
    url = models.CharField(max_length=255)
    name = models.CharField(max_length=20)
    active = models.BooleanField(default=True)
    order_id = models.PositiveSmallIntegerField(unique=True)
    
    class Meta:
        ordering = ['order_id']