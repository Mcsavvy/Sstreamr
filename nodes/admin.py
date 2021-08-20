from django.contrib import admin
from . import models

# Register your models here.

@admin.register(models.Node)
class NodeDisplay(admin.ModelAdmin):
    list_display = [
        "instagram",
        "user",
    ]

@admin.register(models.Notification)
class NotificationDisplay(admin.ModelAdmin):
    list_display = [
        "node",
        "level",
        "status"
    ]