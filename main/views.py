from django.http.response import JsonResponse
from apps.nodes.models import Notification
from apps.feeds.models import *
from core import render
from django.views.generic import View
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.utils import timezone
from django.core import serializers
from core.decorators import Request, allowed_user, authenticated_user
from core.utils import grid
# Create your views here.


class Main(View):
    def handle_notifications(self, request, node):
        # print(request.GET)
        all_ = sorted(node.notifications.all(), key=lambda n: n.created, reverse=True)
        if "read" in request.GET:
            read = request.GET["read"]
            if read == "all":
                for x in all_:
                    x.status = "R"
                    x.save()
            else:
                for x in all_:
                    if x.id == int(read):
                        x.status = "R"
                        x.save()
                        break
        unread_ = tuple(x for x in all_ if x.status != "R")
        for x in unread_:
            if x.status == "S":
                x.status = "D"
                x.save()
        return render(
            request, "partials/notifications.html", {"notifications": all_, 'unread': len(unread_)}
        )

    def youtube(self, request, node):
        all = Youtubevideo.objects.all()
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
        print('LENGTH OF SLIDE PARENT: ', len(slide.parent))
        print('CURRENT SLIDE: ', slide.slide)
        print('CURRENT SLIDE LENGTH: ', len(slide))
        return render(request, 'feeds/youtube.html', {'slide': slide})

    def instagram(self, request, node):
        all = Instagrampost.objects.all()
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
        print('LENGTH OF SLIDE PARENT: ', len(slide.parent))
        print('CURRENT SLIDE: ', slide.slide)
        print('CURRENT SLIDE LENGTH: ', len(slide))
        return render(request, 'feeds/instagram.html', {'slide': slide})


    def get(self, request):
        node = request.user.node
        if request.isAjax:
            if "notification" in request.GET:
                return self.handle_notifications(request, node)
            elif "youtube" in request.GET:
                return self.youtube(request, node)
            elif "instagram" in request.GET:
                return self.instagram(request, node)
        resp = render(request, "main/landing.html", {'range':range(20)})
        resp['SameSite'] = None
        resp['Secure'] = ''
        return resp

    # @Request.ajax(False)
    @authenticated_user(True)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
