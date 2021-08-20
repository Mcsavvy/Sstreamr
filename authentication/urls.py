from collections import namedtuple
from django.urls import path, include
from . import views

urlpatterns = [
    path('join/', views.Create.as_view(), name='auth.create'),
    path('login/', views.Login.as_view(), name='auth.login'),
    path('logout/', views.Logout.as_view(), name='auth.logout'),
    path( 'edit/', views.Edit.as_view(), name='auth.edit'),
    path('forgot/', views.Forgot.as_view(), name='auth.forgot'),
    path('reset/', views.Reset.as_view(), name='auth.reset'),
    path(
        'redirect/<path:path>/',
        views.Redirect.as_view(),
        name='auth.redirect'
    )
]
