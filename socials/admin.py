from typing import Iterable
from django.contrib import admin
from . import models
from .instagram import MyInstagram
# Register your models here.

@admin.register(models.Instagramprofile)
class InstagramProfileAdmin(admin.ModelAdmin):
    def node(self):
        return self.model.node.user.username

    @admin.action(description='Update instagram profiles in real time')
    def update(self, request, queryset: Iterable[models.Instagramprofile]):
        for o in queryset:
            o.fetch_meta()
        self.message_user(request, 'Updated all instagram profiles', 'info')

    @admin.action(description='Check for users that followed back')
    def verify_followback(self, request, queryset: Iterable[models.Instagramprofile]):
        for o in queryset:
            if MyInstagram.is_followed_by(o):
                o.followed_back = True
            else:
                o.followed_back = False
            o.save()
        self.message_user(request, 'Checked all users for follow back', 'info')

    @admin.action(description='Check for users that are being followed')
    def verify_following(self, request, queryset: Iterable[models.Instagramprofile]):
        for o in queryset:
            if MyInstagram.is_following(o):
                o.is_followed = True
            else:
                o.is_followed = False
            o.save()
        self.message_user(request, 'Checked all users for following', 'info')

    @admin.action(description='Unfollow users that haven\'t followed back')
    def unfollow(self, request, queryset: Iterable[models.Instagramprofile]):
        for o in queryset:
            if not o.followed_back:
                if not MyInstagram.unfollow(o):
                    self.message_user(request, f'Could not unfollow {o.username}', 'error')
                else:
                    self.message_user(request, f'Unfollowed {o.username}', 'success')
            else:
                o.followed_back = True
            o.save()

    @admin.action(description='Follow users that have followed back')
    def follow(self, request, queryset: Iterable[models.Instagramprofile]):
        for o in queryset:
            if o.followed_back:
                if not MyInstagram.follow(o):
                    self.message_user(request, f'Could not follow {o.username}', 'error')
                else:
                    self.message_user(request, f'Followed {o.username}', 'success')

    list_display = [
        'username',
        'node',
        'verified',
        'private',
        'is_followed',
        'followed_back'
    ]
    actions = ['update', 'verify_following', 'verify_followback', 'unfollow', 'follow']
