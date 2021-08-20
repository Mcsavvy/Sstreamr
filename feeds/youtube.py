from nodes.models import Node
from django.db import models
from django.db.utils import IntegrityError
import arrow
import re
from youtube_api import YouTubeDataAPI
from django.conf import settings
import stackprinter
stackprinter.set_excepthook(style='darkbg2')
# Create your models here.

# CONSTANTS
START_DATE = arrow.get(2021, 7, 24).datetime
API = YouTubeDataAPI(settings.YOUTUBE_DATA_API_KEY, verify_api_key=False)

__all__ = [
    'Youtubekeyword',
    'Youtubetag',
    'Youtubechannel',
    'Youtubeplaylist',
    'Youtubevideo'
]

class Youtubekeyword(models.Model):
    keyword = models.TextField()

    def __str__(self):
        return f"{'+'.join(self.keyword.split())}"

    class Meta:
        verbose_name = 'Youtube Keyword'


class Youtubetag(models.Model):
    tag = models.CharField(max_length=30)

    def __str__(self):
        return f"#{self.tag}"

    class Meta:
        verbose_name = 'Youtube Tag'


class Youtubechannel(models.Model):
    channel_id = models.CharField(max_length=50)
    title = models.TextField(blank=True)
    creation_date = models.DateTimeField(blank=True, null=True)
    description = models.TextField(blank=True)
    keywords = models.ManyToManyField(
        to=Youtubekeyword,
        related_name='channels',
        blank=True
    )
    uploads = models.CharField(max_length=50, blank=True)

    def fetch_meta(self):
        print('CHANNEL BEFORE META FETCHED: ', self)
        meta = API.get_channel_metadata(self.channel_id)
        print(f"CHANNEL METADATA FOR {self.channel_id}:", meta.keys())
        self.title = meta['title']
        self.creation_date = arrow.get(meta['account_creation_date']).datetime
        self.description = meta['description']
        if meta.get('keywords', None):
            for kwd in re.split(r'\s?"\s?', meta['keywords']):
                if not kwd:
                    continue
                self.keywords.add(Youtubekeyword.objects.create(
                    keyword=kwd
                ))
        self.uploads = meta['playlist_id_uploads']
        print('CHANNEL AFTER META FETCHED: ', self)
        self.save()

    def fetch_playlists(self):
        api = API
        for pl in api.get_playlists(self.channel_id):
            pl: dict
            print(f"PLAYLIST METADATA FOR {pl['playlist_id']}: ", pl.keys())
            try:
                new = Youtubeplaylist.objects.create(
                    name=pl['playlist_name'],
                    playlist_id=pl['playlist_id'],
                    publish_date=arrow.get(pl['playlist_publish_date']).datetime,
                    channel=self
                )
            except IntegrityError:
                print(f"DUPLICATE PLAYLIST_ID '{pl['playlist_publish_date']}'")
                stackprinter.show_current_exception(style='darkbg2')
                continue

    def get_absolute_url(self):
        return f"https://www.youtube.com/channel/{self.channel_id}"

    class Meta:
        verbose_name = 'Youtube Channel'

    def __str__(self):
        return f"{self.title}"

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, self.__class__):
            return NotImplementedError
        return self.channel_id == o.channel_id

    def __hash__(self):
        return super().__hash__()

    def __ne__(self, o: object) -> bool:
        return not self == o


class Youtubeplaylist(models.Model):
    name = models.TextField()
    playlist_id = models.CharField(max_length=50, unique=True)
    publish_date = models.DateTimeField(null=True, blank=True)
    channel = models.ForeignKey(
        to=Youtubechannel, on_delete=models.CASCADE,
        related_name='playlists',
        blank=True, null=True)

    def get_absolute_url(self):
        return f"https://www.youtube.com/playlist?list={self.playlist_id}"

    def __str__(self):
        return f"{self.name}"

    def fetch_videos(self):
        for video in API.get_videos_from_playlist_id(self.playlist_id):
            try:
                new = Youtubevideo.objects.create(
                    video_id=video['video_id'],
                    playlist=self
                )
            except IntegrityError:
                print(f'DUPLICATE VIDEO_ID "{video["video_id"]}"')
                stackprinter.show_current_exception(style='darkbg2')
                continue
            print('NEW VIDEO BEFORE META FETCHED: ', new)
            new.fetch_meta()
            print('NEW VIDEO AFTER META FETCHED: ', new)

    class Meta:
        verbose_name = 'Youtube Playlist'

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, self.__class__):
            return NotImplementedError
        return self.playlist_id == o.playlist_id

    def __hash__(self):
        return super().__hash__()

    def __ne__(self, o: object) -> bool:
        return not self == o


class Youtubevideo(models.Model):
    video_id = models.CharField(max_length=50, unique=True)
    thumbnail = models.URLField(blank=True, null=True)
    playlist = models.ForeignKey(
        to=Youtubeplaylist, related_name='videos',
        on_delete=models.CASCADE,
        null=True, blank=True)
    created_at = models.DateTimeField(blank=True, null=True)
    title = models.TextField(blank=True)
    description = models.TextField(blank=True)
    tags = models.ManyToManyField(
        to=Youtubetag, related_name='videos', blank=True
    )
    viewers = models.ManyToManyField(
        to=Node, blank=True,
        related_name='viewed_youtube_videos'
    )

    def fetch_meta(self):
        meta = API.get_video_metadata(self.video_id)
        if not meta:
            print(
                f'NO METADATA WAS FETCHED FOR {self.video_id}, LIKELY A PRIVATE VIDEO'
            )
            return self.delete()
        print(f"VIDEO META for {self.video_id}:", meta.keys())
        self.thumbnail = meta['video_thumbnail']
        self.created_at = arrow.get(meta['video_publish_date']).datetime
        self.title = meta['video_title']
        self.description = meta['video_description']
        if meta.get('video_tags', None):
            for tag in meta['video_tags'].split('|'):
                new = Youtubetag.objects.create(tag=tag)
                self.tags.add(new)
        self.save()
        return True

    class Meta:
        verbose_name = 'Youtube Video'

    def human_date(self):
        return arrow.get(self.created_at).humanize()

    def dict(self) -> dict[str, object]:
        attrs = 'video_id', 'title', 'description', 'created_at', 'thumbnail'
        return dict(zip(attrs, map(
            lambda key: getattr(self, key, None),
            attrs
        )))

    def json(self) -> str:
        import json
        dict = self.dict()
        dict['created_at'] = self.human_date()
        return json.dumps(dict)

    def get_absolute_url(self):
        return f"https://www.youtube.com/watch?v={self.video_id}"

    def __str__(self) -> str:
        return f"{self.title}"

    def __gt__(self, other) -> bool:
        if not isinstance(other, self.__class__):
            raise TypeError(
                'Can\'t compare YouTube object to {} object.'.format(
                    type(other)
                )
            )
        if other.created_at:
            if self.created_at:
                return self.created_at > other.created_at
            else:
                return False
        else:
            return True

    def __lt__(self, other) -> bool:
        return not self > other

    def __ge__(self, other) -> bool:
        if not isinstance(other, self.__class__):
            raise TypeError(
                'Can\'t compare YouTube object to {} object.'.format(
                    type(other)
                )
            )
        return self.created_at >= other.created_at

    def __le__(self, other) -> bool:
        return not self >= other

    def __eq__(self, other) -> bool:
        if not isinstance(other, self.__class__):
            raise TypeError(
                'Can\'t compare YouTube object to {} object.'.format(
                    type(other)
                )
            )
        return self.video_id == other.video_id

    def __hash__(self):
        return super().__hash__()

    def __ne__(self, other) -> bool:
        return not self == other