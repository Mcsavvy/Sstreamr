from django.db import models
import instaloader as ig_api
from bug import Bug
from datetime import datetime
from config.settings import BASE_DIR, MEDIA_ROOT

loader = ig_api.Instaloader()
# loader.login('__essntls__', 'hood@ins.com')

# Create your models here.

class Instagram(models.Model):
    '''
    This model represents an instagram user
    '''
    username = models.CharField(max_length=50)
    userid = models.IntegerField()
    bio = models.TextField()
    dp = models.ImageField(upload_to='instagram',null=True, blank=True)
    link = models.URLField()
    verified = models.BooleanField()
    private = models.BooleanField()

    def __repr__(self) -> str:
        return "Instagram(username={}, id={})".format(
            self.username, self.userid
        )
    
    def update(self):
        this = ig_api.Profile.from_id(loader.context, self.userid)
        self.username = this.username
        self.bio = this.biography
        self.link = this.external_url
        self.private = this.is_private
        self.verified = this.is_verified
        if this.profile_pic_url:
            loader.download_pic(
                f'{MEDIA_ROOT}/instagram/{this.username}',
                this.profile_pic_url,
                datetime.now()
            )
            self.dp = f'instagram/{this.username}.jpg'
        self.save()
        return self
    
    @staticmethod
    def add(username: str):
        with Bug(ig_api.ProfileNotExistsException) as bug:
            account = ig_api.Profile.from_username(loader.context, username)
            new = Instagram.objects.create(
                username=username,
                bio=account.biography,
                userid=account.userid,
                link=account.external_url,
                private=account.is_private,
                verified=account.is_verified
            )
            if account.profile_pic_url:
                loader.download_pic(
                    f'{MEDIA_ROOT}/instagram/{username}',
                    account.profile_pic_url,
                    datetime.now()
                )
                new.dp = f'instagram/{username}.jpg'
                new.save()
            return new