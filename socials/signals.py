import os
from django.db.models import signals
from django.dispatch import receiver
from .models import Instagramprofile

@receiver(signals.post_save, sender=Instagramprofile)
def fetch_meta_for_ig_profile(sender: type, instance: Instagramprofile, created: bool, **kwds):
    if not created:
        return print(f'ALREADY EXISTING INSTANCE {instance.username}')
    if instance.user_id:
        return print(f'PROFILE METADATA FOR {instance.username} IS ALREADY BEING FETCHED')
    print(f'MANUALLY FETCHING PROFILE METADATA FOR {instance.username}')
    if not instance.fetch_meta():
        return instance.delete()

@receiver(signals.pre_delete, sender=Instagramprofile)
def delete_image_for_ig_profile(sender: type, instance: Instagramprofile, **kwds):
    if instance.profile_pic:
        if os.path.isfile(instance.profile_pic.path):
            os.remove(instance.profile_pic.path)


    
