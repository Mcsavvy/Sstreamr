from django.db import models
import arrow
from bug import Bug

# Create your models here.

class YouTube(models.Model):
    ID = models.CharField(max_length=50, primary_key=True)
    thumbnail = models.URLField()
    channel = models.CharField(max_length=100)
    channelId = models.CharField(max_length=50)
    createdAt = models.DateTimeField()
    title = models.TextField()
    description = models.TextField()

    def humanDate(self):
        return arrow.get(self.createdAt).humanize()

    def dict(self) -> dict[str, object]:
        attrs = 'ID', 'title', 'description', 'createdAt', 'thumbnail', 'channel', 'channelId'
        return dict(zip(attrs, map(
            lambda key: getattr(self, key, None),
            attrs
        )))

    def json(self) -> str:
        import json
        dict = self.dict()
        dict['createdAt'] = self.humanDate()
        return json.dumps(dict)

    def get_absolute_url(self):
        return "https://www.youtube.com/watch?v=%s" % self.ID

    def __str__(self) -> str:
        return "YoutubeVideo(id={}, title={})".format(
            self.ID, self.title
        )

    def __gt__(self, other) -> bool:
        if not isinstance(other, self.__class__):
            raise TypeError(
                'Can\'t compare YouTube object to {} object.'.format(
                    type(other)
                )
            )
        return self.createdAt > other.createdAt

    def __lt__(self, other) -> bool:
        if not isinstance(other, self.__class__):
            raise TypeError(
                'Can\'t compare YouTube object to {} object.'.format(
                    type(other)
                )
            )
        return self.createdAt < other.createdAt

    def __ge__(self, other) -> bool:
        if not isinstance(other, self.__class__):
            raise TypeError(
                'Can\'t compare YouTube object to {} object.'.format(
                    type(other)
                )
            )
        return self.createdAt >= other.createdAt

    def __le__(self, other) -> bool:
        if not isinstance(other, self.__class__):
            raise TypeError(
                'Can\'t compare YouTube object to {} object.'.format(
                    type(other)
                )
            )
        return self.createdAt <= other.createdAt

    def __eq__(self, other) -> bool:
        if not isinstance(other, self.__class__):
            raise TypeError(
                'Can\'t compare YouTube object to {} object.'.format(
                    type(other)
                )
            )
        return self.ID == other.ID

    def __ne__(self, other) -> bool:
        if not isinstance(other, self.__class__):
            raise TypeError(
                'Can\'t compare YouTube object to {} object.'.format(
                    type(other)
                )
            )
        return self.ID != other.ID

    @staticmethod
    def add(_: dict):
        with Bug() as bug:
            bug.drown('IntegrityError')
            return YouTube.objects.create(
                ID=_['video_id'],
                thumbnail=_['video_thumbnail'],
                channel=_['channel_title'],
                channelId=_['channel_id'],
                createdAt=_['video_publish_date'],
                title=_['video_title'],
                description=_['video_description']
            )
        return "Video Already Exists"