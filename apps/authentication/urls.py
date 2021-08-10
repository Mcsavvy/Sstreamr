from collections import namedtuple
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.Main.as_view(), name='auth.main'),
    path('join/', views.Create.as_view(), name='auth.create'),
    path('login/', views.Login.as_view(), name='auth.login'),
    path('logout/', views.Logout.as_view(), name='auth.logout'),
    path('xevent/', views.XEvents.as_view(), name='auth.xevent'),
    path('blank/<reason>', views.Blank.as_view(), name='auth.blank'),
    # path('captcha/', include('captcha.urls')),
    path(
        'redirect/<path:path>/',
        views.Redirect.as_view(),
        name='auth.redirect'
    )
]
