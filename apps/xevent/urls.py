from django.urls import path, include
from .views import Main

urlpatterns = [
    path('', Main.as_view(), name="xevent.main")
]