import os
from typing import Iterable
import stackprinter
stackprinter.set_excepthook(style='darkbg2')
from django.db import models
from datetime import datetime
from django.conf import settings
from nodes.models import Node
from feeds.instagram import API, SESS, download_thumbnail
from instauto.api.actions.structs import direct, profile
from django.db.utils import IntegrityError
from instauto.helpers.friendships import follow_user, get_followers, get_following, unfollow_user

# Create your models here.

IGPHOTODIR = os.path.join(
    settings.MEDIA_ROOT, 'profiles', 'instagram'
)

class Instagramprofile(models.Model):
    '''
    This model represents an instagram user
    '''
    user_id = models.IntegerField(blank=True, null=True, unique=True)
    username = models.CharField(max_length=50)
    node = models.OneToOneField(to=Node, on_delete=models.CASCADE, related_name='instagram')
    bio = models.TextField(blank=True)
    profile_pic = models.ImageField(upload_to='profiles/instagram',null=True, blank=True)
    external_url = models.URLField(null=True, blank=True)
    verified = models.BooleanField(default=False)
    private = models.BooleanField(default=False)
    # set this to true when user follows back
    is_followed = models.BooleanField(default=False)
    followed_back = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Instagram  Profile'

    def __str__(self) -> str:
        return f"{self.username}"

    def fetch_meta(self) -> bool:
        if self.user_id:
            info = profile.Info(user_id=self.user_id)
        else:
            info = profile.Info(username=self.username)
        try:
            profile_info = API.profile_info(info)
        except:
            return False
        if isinstance(profile_info, int):
            return False
        self.username = profile_info['username']
        self.user_id = profile_info['pk']
        self.private = profile_info['is_private']
        self.verified = profile_info['is_verified']
        if profile_info.get('biography', None):
            self.bio = profile_info['biography']
        if profile_info.get('external_url', None):
            self.external_url = profile_info['external_url']
        if profile_info.get('profile_pic_url', None):
            DP_PATH = os.path.join(IGPHOTODIR, f'{self.user_id}.jpg')
            download_thumbnail(
                profile_info['profile_pic_url'],
                DP_PATH
            )
            self.profile_pic = f'profiles/instagram/{self.user_id}.jpg'
        self.save()
        return True
    
    @classmethod
    def add(cls, username: str, node: Node):
        if not isinstance(username, str):
            raise TypeError(f'{cls.__name__} expects a str[username] as first parameter')
        if not isinstance(node, Node):
            raise TypeError(f'{cls.__name__} expects a node instance as second parameter')
        try:
            new = cls.objects.create(
                username=username,
                node=node
            )
            if new.user_id:
                return new
            else:
                if new.fetch_meta():
                    if new.user_id:
                        return new
        except IntegrityError:
            print(f'DUPLICATE INSTAGRAM PROFILE {username}')

class MyInstagram:
    api = API
    n_following = 50000
    n_followers = 50000
    username = '__essntls__'
    user_id = 24482576556

    @classmethod
    def follow(cls, profile: Instagramprofile) -> bool:
        'follow a given instagram profile'
        return follow_user(cls.api, user_id=profile.user_id)

    @classmethod
    def is_following(cls, profile: Instagramprofile) -> bool:
        'confirms if a given instagram profile is already being followed'
        for user in get_following(cls.api, cls.n_following, user_id=cls.user_id):
            if user.pk == profile.user_id:
                return True
        return False
        
    @classmethod
    def is_followed_by(cls, profile: Instagramprofile) -> bool:
        'confirm if a given instagram profile is following self'
        for user in get_followers(cls.api, cls.n_followers, user_id=cls.user_id):
            if user.pk == profile.user_id:
                return True
        return False

    @classmethod
    def direct_message(cls, profile: Instagramprofile, msg: str) -> bool:
        'send a direct message to a given instagram profile'
        assert isinstance(msg, str)
        msg = direct.Message(msg, recipients=[[profile.user_id]])
        cls.api.direct_send(msg)



    @classmethod
    def unfollow(cls, profile: Instagramprofile) -> bool:
        'unfollows a given instagram profile'
        return unfollow_user(cls.api, user_id=profile.user_id)
        
