import os
from django.db.models.signals import post_save, pre_delete
import threading
from django.dispatch import receiver
from .models import (
    Youtubeplaylist, Youtubechannel, Youtubevideo,
    Instagrampost
)
import stackprinter
stackprinter.set_excepthook(style='darkbg2')

@receiver(post_save, sender=Youtubechannel)
def channel_fetch_meta_and_playlist(sender: type, instance: Youtubechannel, created:bool, **kwds):
    if not created: return print(f'ALREADY EXISTING CHANNEL {instance.channel_id}')
    print('NEW CHANNEL CREATED')
    print('FETCHING ALL CHANNEL PLAYLISTS AND CHANNEL META-DATA')
    instance.fetch_meta()
    t = threading.Thread(target=instance.fetch_playlists)
    t.start()
    instance.save()



@receiver(post_save, sender=Youtubeplaylist)
def playlist_fetch_meta_and_videos(sender: type, instance: Youtubeplaylist, created:bool, **kwds):
    if not created: return print(f'ALREADY EXISTING PLAYLIST {instance.playlist_id}')
    if instance.channel:
        return print('PLAYLIST IS ALREADY BEING POPULATED WITH VIDEOS')
    print('MANUALLY POPULATING PLAYLIST WITH VIDEOS')
    instance.fetch_videos()

@receiver(post_save, sender=Youtubevideo)
def video_fetch_meta(sender: type, instance: Youtubevideo, created:bool, **kwds):
    if not created: return print(f'ALREADY EXISTING VIDEO {instance.video_id}')
    if instance.playlist:
        return print('VIDEO META-DATA IS ALREADY BEING FETCHED')
    print('MANUALLY FETCHING VIDEO META-DATA')
    if not instance.fetch_meta():
        instance.delete()

@receiver(post_save, sender=Instagrampost)
def post_fetch_meta(sender: type, instance: Instagrampost, created: bool, **kwds):
    if not created: return print(f'ALREADY EXISTING POST {instance.post_id}')
    if instance.thumbnail:
        return print('POST META-DATA IS ALREADY BEING FETCHED')
    print('MANUALLY FETCHING POST METADATA')
    if not instance.fetch_meta():
        instance.delete()


@receiver(pre_delete, sender=Instagrampost)
def post_delete_image(sender: type, instance: Instagrampost, **kwds):
    if instance.thumbnail:
        if os.path.isfile(instance.thumbnail.path):
            os.remove(instance.thumbnail.path)
