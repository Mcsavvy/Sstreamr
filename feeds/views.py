from re import U
from django import http
from django.http.response import JsonResponse
from nodes.models import Notification, User
from core import render
from django.shortcuts import render as render_
from django.views.generic import View
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.utils import timezone
from django.core import serializers
from core.decorators import Request, allowed_user, authenticated_user
from core.utils import grid
from authentication.forms import EditAccount
# Create your views here.

class Main(View):
    @authenticated_user(True)
    def get(self, request)