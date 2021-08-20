from django.db import models
from django.contrib.auth.models import User
from .profile import clean_email, hash_email
from django.db.utils import IntegrityError
# Create your models here.


class Node(models.Model):
    user = models.OneToOneField(
        User,
        related_name="node",
        on_delete=models.CASCADE
    )

    def dp(self):
        try:
            self.instagram
            if self.instagram.profile_pic:
                return self.instagram.profile_pic.url
        except: pass
        if self.user.email:
            token = self.user.email
        else:
            token = self.user.username
        return "https://www.gravatar.com/avatar/{}?d=retro".format(
            hash_email(clean_email(token))
        )

    def notify(self, message, level='info', action: str = '', href=None, onclick=None):
        if level not in ('info', 'warning', 'success', 'error'):
            raise TypeError('"%s" is not an accepted notification level.')
        new = Notification.objects.create(
            message=message,
            level=level,
            node=self
        )
        if action:
            if not any((href, onclick)):
                raise IntegrityError(f'no onclick or href specified for {action}')
            new.action, new.href, new.onclick = action, href, onclick
            new.save()

    def __str__(self):
        return self.user.username


class Notification(models.Model):
    class LEVELS(models.TextChoices):
        INFO = 'info', 'Information'
        WARNING = 'warning', 'Warning'
        SUCCESS = 'success', 'Success'
        ERROR = 'error', 'Error'

    class STATUSES(models.TextChoices):
        SENT = 'S', 'Sent'
        DELIVERED = 'D', 'Delivered'
        READ = 'R', 'Read'

    message = models.TextField()
    node = models.ForeignKey(
        Node,
        related_name="notifications",
        on_delete=models.CASCADE
    )
    level = models.CharField(
        max_length=22,
        choices=LEVELS.choices,
        default=LEVELS.INFO
    )
    created = models.DateTimeField(
        auto_now_add=True
    )
    status = models.CharField(
        max_length=10,
        choices=STATUSES.choices,
        default=STATUSES.SENT
    )
    action = models.CharField(max_length=50, blank=True)
    href = models.URLField(null=True, blank=True)
    onclick = models.TextField(null=True, blank=True)

    def __str__(self) -> str:
        return f'Notification(for={self.node}, type={self.level}, status={self.status})'

    def save(self, **kwds):
        if self.action:
            if not any((self.href, self.onclick)):
                raise IntegrityError(f'no onclick or href specified for {self.action}')
        super().save(**kwds)