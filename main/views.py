from re import U
from django import http
from django.http.response import JsonResponse
from nodes.models import Notification, User
from feeds.models import *
from core import render
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


class Feeds(View):
    def youtube(self, request, node):
        all = Youtubevideo.objects.all()
        for video in all:
            video.viewers.add(node)
        current_slide = int(request.GET.get('s', 1))
        amount = int(request.GET.get('c', 20))
        sorted_by_date = sorted(
            all,
            reverse=True
        )
        slide = grid(
            sorted_by_date, width=amount, spillover=True,
            slide=current_slide, fillempty=object
        )
        # print('LENGTH OF SLIDE PARENT: ', len(slide.parent))
        # print('CURRENT SLIDE: ', slide.slide)
        # print('CURRENT SLIDE LENGTH: ', len(slide))
        return render(request, 'feeds/youtube.html', {'slide': slide})

    def instagram(self, request, node):
        all = Instagrampost.objects.all()
        for post in all:
            post.viewers.add(node)
        current_slide = int(request.GET.get('s', 1))
        amount = int(request.GET.get('c', 20))
        sorted_by_date = sorted(
            all,
            reverse=True
        )
        slide = grid(
            sorted_by_date, width=amount, spillover=True,
            slide=current_slide, fillempty=object
        )
        # print('LENGTH OF SLIDE PARENT: ', len(slide.parent))
        # print('CURRENT SLIDE: ', slide.slide)
        # print('CURRENT SLIDE LENGTH: ', len(slide))
        return render(request, 'feeds/instagram.html', {'slide': slide})

    def get(self, request):
        node = request.user.node
        if request.isAjax:
            if "youtube" in request.GET:
                return self.youtube(request, node)
            elif "instagram" in request.GET:
                return self.instagram(request, node)
        resp = render(request, "main/feeds.html", {'range':range(20)})
        resp['SameSite'] = None
        resp['Secure'] = ''
        return resp

    @authenticated_user(True, login_url='main.landing')
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

class Profile(View):
    @authenticated_user(True)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        user = request.user
        node = user.node
        notifications = sorted(node.notifications.all(), key=lambda n: n.created, reverse=True)
        initial_data = {
            field: getattr(user, field) for field in ('username', 'email')
        }
        context = {
            'form': EditAccount(initial=initial_data),
            'notifications': notifications
        }
        return render(request, 'main/profile.html', context=context)

    def post(self, request):
        user = request.user
        node = user.node
        notifications = sorted(node.notifications.all(), key=lambda n: n.created)
        initial_data = {
            field: getattr(user, field) for field in ('username', 'email')
        }
        bound_form = EditAccount(request.POST,initial=initial_data)
        context = {
            'form': bound_form,
            'notifications': notifications
        }
        if bound_form.is_valid():
            data = bound_form.cleaned_data
            if bound_form.has_changed():
                if 'oldpassword' in bound_form.changed_data and data['oldpassword']:
                    if 'newpassword' in bound_form.changed_data and data['newpassword']:
                        if data['oldpassword'] == data['newpassword']:
                            messages.warning(
                                request,
                                'specify an new password for your account or leave it blank??title=Passwords are the same'
                            )
                            return redirect('main.profile')
                        if not user.check_password(data['oldpassword']):
                            bound_form.add_error('oldpassword', 'old password is incorrect')
                        else:
                            user.set_password(data['newpassword'])
                    else:
                        bound_form.add_error('newpassword', 'new password cannot be empty')
                if 'username' in bound_form.changed_data:
                    if User.objects.filter(username=data['username']):
                        bound_form.add_error('username', 'this username is not available')
                    else:
                        user.username = data['username']
                if 'email' in bound_form.changed_data:
                    if User.objects.filter(email=data['email']):
                        bound_form.add_error('username', 'this username is not available')
                    else:
                        user.email = data['email']
                if bound_form.errors:
                    return render(request, 'main/profile.html', context=context)
                success_mesage = 'The following were updated;<br>'
                if 'username' in bound_form.changed_data:
                    success_mesage += f'username: {data["username"]}<br>'
                if 'email' in bound_form.changed_data:
                    success_mesage += f'email: {data["email"]}<br>'
                if 'newpassword' in bound_form.changed_data:
                    success_mesage += f'password: {data["newpassword"][:2]}{"*" * (len(data["newpassword"])  - 4)}{data["newpassword"][-2:]}'
                user.save()
                login(request, user)
                messages.success(
                    request,
                    f'{success_mesage}??title={user.username}, your profile has been updated!'
                )
                return redirect('main.profile')
            else:
                messages.warning(
                    request,
                    "this is because you changed nothing in the form??title=Nothing was changed"
                )
                return redirect('main.profile')
                        
        else:
            return render(request, 'main/profile.html', context=context)
            

class Landing(View):
    def ajax(self, request):
        return JsonResponse(
            {"message": "Ajax requests not allowed.", "level": "warning"}
        )
    
    @Request.ajax(False, view_func=ajax)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request):
        return render(request, "main/landing.html")