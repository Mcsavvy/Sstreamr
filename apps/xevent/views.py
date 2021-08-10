from django.views.generic import View
from django.http import JsonResponse
from core.decorators import Request, authenticated_user
from core.caching import CachedObject
from ..socials.instagram import Instagramprofile, MyInstagram
from threading import Thread

# Create your views here.
class Main(View):
    def non_ajax(self):
        return JsonResponse({
            'message': 'Request not understood',
            'level': 'error'
        })

    @authenticated_user(True)
    def set_instagram(self, request, xevent=None, xargs=None):
        node = request.user.node
        try:
            node.instagram
            node.notify('We noticed you tried to set your instagram twice.', 'warning')
            return JsonResponse({
                'message': 'We already have your instagram.??title=Hey {}...&&type=ig'.format(
                    request.user.username.title()
                )
            })
        except: pass
        new_ig = Instagramprofile.add(xargs['username'].strip(), node)
        if new_ig:
            node.notify(f'"{xargs["username"]}" has been set as your instagram account.', 'success')
            def follow_node():
                if MyInstagram.follow(new_ig):
                    node.notify(
                        f'We have followed you on ig, follow back to confirm ownership of the account. You would receive updates only after this.'
                    )
                else:
                    node.notify(
                        f'We could not follow you on ig, this could be caused by your instagram privacy settings. we would notify you when it is resolved'
                    )
            Thread(target=follow_node).start()
            return JsonResponse({
                'message': '{}, your instagram account has been added.??title=Verified&&type=ig'.format(
                    request.user.username.title()
                ),
                'reload': True,
            })
        else:
            node.notify(
                f'We could not verify that "{xargs["username"]}" is a valid instagram account.',
                'error'
            )
            return JsonResponse({
                'message': (
                    '"{}" instagram could not be found,'
                    ' make sure you typed in your username correctly.'
                    '??title=Hey {}...&&type=ig'.format(
                        xargs['username'],
                        request.user.username.title()
                    )
                ),
                'reload': False,
            })
    
    @authenticated_user(True)
    def remove_instagram(self, request):
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
        return JsonResponse({})

    @authenticated_user(True)
    def update_instagram(self, request):
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
        return JsonResponse({})

    @Request.restrict(allowed_methods=['GET'])
    @Request.ajax(True, non_ajax)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    @Request.on('set:instagram', set_instagram)
    @Request.on('update:instagram', update_instagram)
    @Request.on('remove:instagram', remove_instagram)
    def get(self, request):
        return JsonResponse({})