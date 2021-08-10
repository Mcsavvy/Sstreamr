from .models import User, Node
from django.dispatch import receiver
from django.contrib.auth.models import Group
from django.db.models.signals import post_save

@receiver(post_save, sender=User)
def nodify(sender: type, instance: User, created: bool,  **kwargs) -> Node:
    if not created:
        return print('ALREADY EXISTING USER')
    node = Node.objects.get_or_create(
        user=instance
    )
    root, _ = Group.objects.get_or_create(name='root')
    streamr, _ = Group.objects.get_or_create(name='streamer')
    if instance.is_superuser:
        instance.groups.add(root)
    else:
        instance.groups.add(streamr)
    instance.save()