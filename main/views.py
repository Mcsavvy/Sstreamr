from nodes.models import Notification
from core import render
from django.views.generic import View
from django.shortcuts import redirect
from core.models import User, Nodes, nodify
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.utils import timezone
from django.core import serializers
from core.decorators import Request, allowed_user, authenticated_user
from core.models import YouTubes
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
                    x.status = "read"
                    x.save()
            else:
                for x in all_:
                    if x.id == int(read):
                        x.status = "read"
                        x.save()
                        break
        unread_ = tuple(x for x in all_ if x.status != "read")
        for x in unread_:
            if x.status == "sent":
                x.status = "delivered"
                x.save()
        read_ = tuple(x for x in all_ if x.status == "read")
        return render(
            request, "partials/notifications.html", {"notifications": (unread_, read_)}
        )

    def get(self, request):
        node = request.user.node
        if request.isAjax:
            if "notification" in request.GET:
                return self.handle_notifications(request, node)
        all_youtube_videos = YouTubes()
        youtube_videos_sorted_by_date = sorted(
            all_youtube_videos, key=lambda vid: vid.createdAt,
            reverse=True
        )
        youtube_videos_grid = grid(
            youtube_videos_sorted_by_date, num_of_cols=6, spillover=True
        )

        context = {
            "youtube": youtube_videos_grid[:10]
        }
        response = render(request, "main/landing.html", context)
        return response

    # @Request.ajax(False)
    @authenticated_user(True)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
