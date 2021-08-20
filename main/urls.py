from django.urls import path, include, re_path
from . import views

urlpatterns = [
    path('', views.Feeds.as_view(), name="main.feeds"),
    path('landing/', views.Landing.as_view(), name='main.landing'),
    path('profile/', views.Profile.as_view(), name='main.profile'),
]
