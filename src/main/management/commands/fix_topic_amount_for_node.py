from django.core.management.base import BaseCommand

from main.models import Node


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        
        nodes = Node.objects.all()
        for n in nodes:
            real_amount = n.topics.count()
            if n.topic_amount != real_amount:
                n.topic_amount = real_amount
                n.save()
                
                self.stdout.write('{0} updated'.format(n.name))