from django.urls import path, include
from . import views

urlpatterns = [
    path('instagram/', views.Instagram.as_view(), name="xevent.instagram"),
    path('notifications/', views.Notification.as_view(), name="xevent.notifications"),
    path('feeds/', views.Feeds.as_view(), name='xevent.feeds'),
    
]