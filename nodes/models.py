from django.db import models
from django.contrib.auth.models import User
from django.db.models.deletion import CASCADE
from django.db.models.lookups import In
from django.utils import timezone
from .profile import clean_email, hash_email
from collections import defaultdict
# Create your models here.
from socials.models import Instagram


class Node(models.Model):
    user = models.OneToOneField(
        User,
        related_name="node",
        on_delete=models.CASCADE
    )
    instagram = models.OneToOneField(
        Instagram,
        related_name='node',
        blank=True, null=True,
        on_delete=models.SET_NULL
    )
    # settings = models.OneToOneField(
    #     'Settings',
    #     on_delete=models.CASCADE,
    #     related_name='node'
    # )

    @property
    def dp(self):
        if self.instagram and self.instagram.dp:
            return self.instagram.dp.url
        if self.user.email:
            token = self.user.email
        else:
            token = self.user.username
        return "https://www.gravatar.com/avatar/{}".format(
            hash_email(clean_email(token))
        )

    def notify(self, message, level='info'):
        if level not in Notification.levels:
            raise TypeError('"%s" is not an accepted notification level.')
        Notification.objects.create(
            message=message,
            level=level,
            node=self
        )

    def __str__(self):
        return self.user.username


class Notification(models.Model):
    levels = 'info', 'warning', 'success', 'error'
    statuses = 'sent', 'delivered', 'read'
    message = models.TextField()
    node = models.ForeignKey(
        Node,
        related_name="notifications",
        on_delete=models.CASCADE
    )
    level = models.CharField(
        max_length=22,
        default=levels[0]
    )
    created = models.DateTimeField(
        auto_now_add=True
    )
    status = models.CharField(
        max_length=10,
        default=statuses[0]
    )

    def __str__(self) -> str:
        return f'Notification(for={self.node}, type={self.level}, status={self.status})'
    

# class Settings(models.Model):
#     all = defaultdict(lambda key: False)
#     '''
#     Settings objects
#     '''

#     this = models.TextField()
#     modified = models.DateTimeField(auto_now=True)