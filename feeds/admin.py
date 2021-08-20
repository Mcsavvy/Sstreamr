from typing import Iterable
from django.contrib import admin
from . import models
import arrow
# Register your models here.


@admin.register(models.Youtubekeyword)
class YoutubeKeyword(admin.ModelAdmin):
    def num_of_channels(self, o):
        return len(o.channels.all())

    list_display = ['__str__', 'num_of_channels']

@admin.register(models.Youtubetag)
class YoutubeTag(admin.ModelAdmin):
    def num_of_videos(self, o):
        return len(o.videos.all())
    
    list_display = ['__str__', 'num_of_videos']

@admin.register(models.Youtubechannel)
class YoutubeChannel(admin.ModelAdmin):
    def playlists(self, o):
        return len(o.playlists.all())

    def created(self, o):
        if o.creation_date:
            return arrow.get(o.creation_date).humanize()
        return 'Unknown'

    @admin.action(description='Update youtube channel metadata')
    def fetch_metadata(self, request, queryset: Iterable[models.Youtubechannel]):
        for o in queryset:
            o.fetch_meta()
        self.message_user(request, 'Updated metadata for selected channel[s]', 'info')

    @admin.action(description='Fetch all channel playlists')
    def fetch_playlist(self, request, queryset: Iterable[models.Youtubechannel]):
        for o in queryset:
            o.fetch_playlists()
        self.message_user(request, 'Updated playlists for selected channel[s]', 'info')

    list_display = [
        'channel_id',
        'title',
        'created',
        'playlists',
        'uploads'
    ]

    actions = ['fetch_metadata', 'fetch_playlist']

@admin.register(models.Youtubeplaylist)
class YoutubePlaylist(admin.ModelAdmin):
    def videos(self):
        return len(self.videos.all())

    def created(self):
        if self.publish_date:
            return arrow.get(self.publish_date).humanize()
        return 'Unknown'

    def channel(self):
        return self.channel.title.title() if self.channel else 'Generic Channel'

    @admin.action(description='Fetch all playlist videos')
    def fetch_videos(self, request, queryset: Iterable[models.Youtubeplaylist]):
        for o in queryset:
            o.fetch_videos()
        self.message_user(request, 'Updated metadata for selected video[s]', 'info')
        
    list_display = [
        'playlist_id',
        'name',
        created,
        videos,
        channel
    ]

    actions = ['fetch_videos']

@admin.register(models.Youtubevideo)
class YoutubeVideo(admin.ModelAdmin):
    def playlist(self, o):
        return o.playlist.name.title() if o.playlist else 'Generic Playlist'
    
    def created(self, o):
        if o.created_at:
            return arrow.get(o.created_at).humanize()
        return 'Unknown'

    @admin.action(description='Update youtube video metadata')
    def fetch_metadata(self, request, queryset: Iterable[models.Youtubevideo]):
        for o in queryset:
            o.fetch_meta()
        self.message_user(request, 'Updated metadata for selected video[s]', 'info')

    list_display = [
        'video_id',
        'title',
        'created',
        'playlist'
    ]
    actions = ['fetch_metadata']

@admin.register(models.Instagrampost)
class InstagramPost(admin.ModelAdmin):
    def created(self, o):
        if o.created_at:
            return arrow.get(o.created_at).humanize()
        return 'Unknown'

    @admin.action(description='Update instagram post metadata')
    def fetch_metadata(self, request, queryset: Iterable[models.Instagrampost]):
        for o in queryset:
            o.fetch_meta()
        self.message_user(request, 'Updated metadata for selected video[s]', 'info')
        
    list_display = [
        'post_id',
        'title',
        'created'
    ]

    actions = ['fetch_metadata']
