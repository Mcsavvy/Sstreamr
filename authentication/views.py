from core import render
from django.views.generic import View
from django.shortcuts import redirect
from core.utils import arg_parser
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core import serializers
from core.decorators import Request, authenticated_user
from django.http import JsonResponse
import re
from .forms import CreateAccount, LoginAccount, ForgotAccount, EditAccount
from nodes.models import User, Node

# Create your views here.


class Edit(View):
    def get(self, request):
        context = {'form': EditAccount()}
        return render(request, 'auth/edit.html', context=context)

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

class Forgot(View):
    def get(self, request):
        context = {'form':ForgotAccount()}
        return render(request, 'auth/forgot.html', context=context)

class Reset(View):
    def get(self, request):
        return render(request, 'auth/reset.html')

class Create(View):
    def get(self, request):
        context = {'form': CreateAccount()}
        return render(request, "auth/join.html", context=context)

    @Request.ajax(False)
    @authenticated_user(False)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request):
        bound_form = CreateAccount(request.POST)
        timeout, errors = 2000, []
        if not bound_form.is_valid():
            context = {'form': bound_form}
            return render(request, "auth/join.html", context=context)
        else:
            data = bound_form.cleaned_data
            if User.objects.filter(username=data['username']):
                bound_form.add_error('username', 'username is not available')
            if User.objects.filter(email=data['email']):
                bound_form.add_error('email', 'this email is linked to another account')
            if data['password'] != data['password2']:
                messages.error(request, 'the passwords you entered do not match??title=We noticed that...')
                context = {'form': bound_form}
                return render(request, "auth/join.html", context=context)
            if bound_form.errors:
                context = {'form': bound_form}
                return render(request, "auth/join.html", context=context)
            new = User.objects.create(
                username=data['username'],
                email=data['email']
            )
            new.set_password(data['password'])
            new.save()
            new.node.notify(
                f'Welcome to unlimited streaming {new.username}, feel free to indulge your senses'
            )
            new.node.notify(
                'Take control of the switches',
                action='<i class\'fas fa-bulb\'></i>',
                onclick='Theme.toggle()'
            )
            new.node.notify(
                'Ssteamr works best if you have an instagram account',
                action='add instagram',
                onclick="$('a.nav-link[href=\'#instagram\']').click()"
            )
            messages.success(
                request,
                f"{new.username}, you are now one of our streamrs.??title=WELCOME ABODE",
            )
            login(request, new)
            return redirect("main.profile")

class Login(View):
    def get(self, request):
        context = {'form': LoginAccount()}
        return render(request, "auth/login.html", context=context)

    def post(self, request):
        bound_form = LoginAccount(request.POST)
        if not bound_form.is_valid():
            context = {'form': bound_form}
            return render(request, "auth/login.html", context=context)
        else:
            user = authenticate(
                request,
                username=bound_form.cleaned_data['login'],
                password=bound_form.cleaned_data['password']
            )
            if user:
                login(request, user)
                messages.info(
                    request,
                    f"let us show you what you missed..??title=Welcome back {user.username}!",
                )
                return redirect("main.feeds")
            user = authenticate(
                request,
                email=bound_form.cleaned_data['login'],
                password=bound_form.cleaned_data['password']
            )
            if user:
                login(request, user)
                messages.info(
                    request,
                    f"let us show you what you missed..??title=Welcome back {user.username}!",
                )
                return redirect("main.feeds")
            else:
                messages.error(
                    request, "we could not validate your credentials.??title=Hey sstreamr"
                )
                return redirect("auth.login")

    @authenticated_user(False)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

class Logout(View):
    def get(self, request):
        logout(request)
        return redirect("main.landing")

    @authenticated_user(True)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

class Redirect(View):
    def non_ajax_post(self, request, *args, **kwargs):
        return JsonResponse(
            {"message": "Message could not be understood", "level": "error"}
        )

    def do_redirect(self, request, *args, **kwargs):
        url = str(kwargs['path'])
        if not (url.startswith('http') or url.startswith('/')):
            url = "/" + url
        return JsonResponse({"url": url})

    @Request.on("do:redirect", do_redirect)
    def get(self, request, path):
        return render(request, "auth/redirect.html")

    @Request.ajax(True, view_func=non_ajax_post)
    def post(self, request):
        return JsonResponse({})