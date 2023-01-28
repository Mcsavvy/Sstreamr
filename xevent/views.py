import json
from django.http.response import HttpResponseBadRequest, HttpResponseBase, JsonResponse
from django.views.generic import View
from django import http
from typing import Any
from core.decorators import Request, authenticated_user
from core.caching import CachedObject
from socials.instagram import Instagramprofile, MyInstagram
from threading import Thread
from nodes.models import Notification as notification
from django.shortcuts import render as render_
from core import render
from feeds.models import Youtubevideo, Instagrampost

# Create your views here.
class Base(View):
    """
    This is the base view for  x-events
    x-events are http request-response cycles between javascript and python
    the browser sends a request with is parsed by python and a json-response is sent back with is parsed by the browser
    """
    def non_ajax_request(self, request):
        'non-ajax requests are set to this page'
        return http.JsonResponse({
            'message': 'request not understood',
            'level': 'error'
        })

    @Request.ajax(True, non_ajax_request)
    def dispatch(self, request: http.HttpRequest, *args: Any, **kwargs: Any) -> HttpResponseBase:
        return super().dispatch(request, *args, **kwargs)

class Main(Base):
    def notifications(self, request, xevent, xargs):
        if xargs['action'] == 'deliver':
            print('ids: ', xargs['ids'])
            for pk in xargs['ids']:
                try:
                    target = Notification.objects.get(id=pk)
                    target.status = 'D'
                    target.save()
                except Notification.DoesNotExist: continue
        elif xargs['action'] == 'read':
            print('id: ', xargs['id'])
            try:
                target = Notification.object.get(id=xargs['id'])
                target.status = 'R'
                target.save()
            except Notification.DoesNotExist: pass
        return http.JsonResponse({})

    def get(self, request):
        return http.JsonResponse({})

class Notification(Base):
    @Request.on('deliver', 'deliver')
    @Request.on('read', 'read')
    @Request.on('get:count', 'getcount')
    def get(self, request):
        import arrow
        try:
            node = request.user.node
        except:
            return self.non_ajax_request(request)
        notifications = sorted(node.notifications.all(), key=lambda n: n.created)
        return render(request, 'partials/notifications.html', context={'notifications': notifications})

    def getcount(self, request):
        node = request.user.node
        return http.JsonResponse(dict(
            all=len(node.notifications.all()),
            sent=len(node.notifications.filter(status='S')),
            delivered=len(node.notifications.filter(status='D')),
        ))
    
    def deliver(self, request, ids=[]):
        print('ids to deliver:', ids)
        for id in ids:
            if request.user.node.notifications.filter(id=id).exists():
                target = notification.objects.get(id=id)
                target.status = 'D'
                target.save()

        return http.JsonResponse({})

    def read(self, request, ids=[]):
        print('ids to read:', ids)
        for id in ids:
            if request.user.node.notifications.filter(id=id).exists():
                target = notification.objects.get(id=id)
                target.status = 'R'
                target.save()
        return http.JsonResponse({})

class Instagram(Base):
    @authenticated_user(True)
    def add(self, request, username=None):
        node = request.user.node
        try:
            node.instagram
            node.notify(
                'We noticed you tried to set your instagram twice.',
                'warning',
                action='your instagram',
                href=f'https://www.instagram.com/{node.instagram.username}'
            )
            return http.JsonResponse({
                'message': 'We already have your instagram.??title=Hey {}...&&type=ig'.format(
                    request.user.username.title()
                )
            })
        except: pass
        new = Instagramprofile.add(username, node)
        if new:
            node.notify(
                f'"{username}" has been set as your instagram account.',
                'success',
                action='view it',
                href=f'https://www.instagram.com/{username}'
            )
            def follow_node():
                if MyInstagram.follow(new):
                    node.notify(
                        f'We have followed you on instagram, follow back to confirm ownership of the account. You would start receiving updates after this.'
                    )
                else:
                    node.notify(
                        f'We could not follow you on instagram, this could be caused by your instagram privacy settings. we would notify you when it is resolved'
                    )
            # Thread(target=follow_node).start()
            return http.JsonResponse({
                'message': '{}, your instagram account has been added.??title=Verified&&type=ig'.format(
                    node.user.username.title()
                ),
                'reload': True,
            })
        else:
            node.notify(
                f'We could not verify that "{username}" is a valid instagram account.',
                'error'
            )
            return http.JsonResponse({
                'message': (
                    '"{}" instagram could not be found,'
                    ' make sure you typed in your username correctly.'
                    '??title=Hey {}...&&type=ig'.format(
                        username,
                        node.user.username.title()
                    )
                ),
                'reload': False,
            })
    
    @authenticated_user(True)
    def remove(self, request):
        if request.user.is_authenticated:
            node = request.user.node
            try:
                node.instagram
                node.instagram.delete()
                node.notify(
                    'You instagram was removed. You would no longer receive updates from us if you were already doing so.'
                )
            except:
                node.notify(
                    'Your instagram is not set.',
                    'warning'
                )
        return http.JsonResponse({})

    @authenticated_user(True)
    def update(self, request):
        if request.user.is_authenticated:
            node = request.user.node
            try:
                node.instagram
                node.instagram.fetch_meta()
                node.notify(
                    'Your instagram is now up to date.', 'success'
                )
            except:
                node.notify(
                    'Your instagram is not set.',
                    'warning'
                )
        return http.JsonResponse({})

    @Request.on('add', 'add')
    @Request.on('update', 'update')
    @Request.on('remove', 'remove')
    def get(self, request):
        return http.JsonResponse({})

class Feeds(Base):
    @authenticated_user(True)
    @Request.on('get:count', 'getcount')
    @Request.on('get:item', 'getitem')
    def get(self, request):
        return http.HttpResponseBadRequest()

    def getcount(self, request):
        node = request.user.node
        youtube = Youtubevideo.objects.all()
        instagram = Instagrampost.objects.all()
        return http.JsonResponse(dict(
            all_youtube_videos=len(youtube),
            all_instagram_posts=len(instagram),
            viewed_youtube_videos=len([v for v in youtube if v in node.viewed_youtube_videos.all()]),
            viewed_instagram_posts=len([p for p in instagram if p in node.viewed_instagram_posts.all()])
        ))

    def getitem(self, request, type, id, render_as='json'):
        if type in ['ig', 'instagram']:
            return self.instagram_item(request, id, render_as)
        return JsonResponse({})
    
    def instagram_item(self, request, id, render_as):
        target = Instagrampost.objects.filter(id=id)
        if not target:
            if render_as == 'html':
                return HttpResponseBadRequest()
            return JsonResponse({})
        t = target[0]
        if render_as == 'html':
            return render_(request, 'feeds/partials/instagram-item.html', context={'post': t})
        return JsonResponse(dict(
            post_id=t.post_id,
            embed=t.embed_src,
            raw_title=t.title,
            title=t.title_parsed(),
            thumbnail=t.thumbnail.url,
            viewed=request.user.node in t.viewers.all()
        ))
