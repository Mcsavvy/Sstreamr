from django.contrib import admin
from . import models

# Register your models here.


class NodeDisplay(admin.ModelAdmin):
    list_display = [
        "instagram",
        "user",
    ]


class NotificationDisplay(admin.ModelAdmin):
    list_display = [
        "node",
        "level",
        "status"
    ]


admin.site.register(
    models.Node,
    NodeDisplay
)
admin.site.register(
    models.Notification,
    NotificationDisplay
)
