from django.db import models
from django.contrib.auth.models import User
from .profile import clean_email, hash_email
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

    def notify(self, message, level='info'):
        if level not in ('info', 'warning', 'success', 'error'):
            raise TypeError('"%s" is not an accepted notification level.')
        Notification.objects.create(
            message=message,
            level=level,
            node=self
        )

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

    def __str__(self) -> str:
        return f'Notification(for={self.node}, type={self.level}, status={self.status})'
    

# class Settings(models.Model):
#     all = defaultdict(lambda key: False)
#     '''
#     Settings objects
#     '''

#     this = models.TextField()
#     modified = models.DateTimeField(auto_now=True)