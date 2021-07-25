from django.http import HttpResponse, HttpRequest
from django.shortcuts import redirect
from . import render, error
from .utils import Attr, arg_parser
from .models import User
from .random_fields import Random
from .caching import CachedObject, dbcache
import typing
from inspect import signature
from functools import wraps


def allowed_user(allowed_groups: typing.Iterable = []):
    """
    Restrict user by groups
    """

    def decorator(view_func):
        context = {
            "suggested": ["This page maybe be restricted to a particular group."],
            "name": 405,
            "reason": "Access Denied",
            "info": f"Allowed-Groups ({':'.join(allowed_groups)})",
        }
        if "self" in signature(view_func).parameters:

            def wrapper_func(self, request, *args, **kwargs):

                if request.user.is_authenticated and request.user.groups.exists():
                    for grp in request.user.groups.all():
                        if grp.name in allowed_groups:
                            return view_func(self, request, *args, **kwargs)
                return error(request, context, status=405)

        else:

            def wrapper_func(request, *args, **kwargs):
                if request.user.is_authenticated and request.user.groups.exists():
                    for grp in request.user.groups.all():
                        if grp.name in allowed_groups:
                            return view_func(request, *args, **kwargs)
                return error(request, context, status=405)

        return wrapper_func

    return decorator


def authenticated_user(
    authenticated: bool = False,
    login_url: str = "/auth/redirect//auth/",
    redirect_url: str = "/auth/redirect///",
):
    """
    restrict view to Authenticated users
    or None-Authenticated users
    """
    if not ((authenticated and login_url) or (not authenticated and redirect_url)):
        raise RuntimeError("Provide a url for either login or redirect")

    def wrapper(view):
        if "self" in signature(view).parameters:
            @wraps(view)
            def inner(self, request, *args, **kwds):
                if authenticated:
                    if request.user.is_authenticated:
                        return view(self, request, *args, **kwds)
                    return redirect(login_url)
                if request.user.is_authenticated:
                    return redirect(redirect_url)
                return view(self, request, *args, **kwds)

        else:
            @wraps(view)
            def inner(request, *args, **kwds):
                if authenticated:
                    if request.user.is_authenticated:
                        return view(request, *args, **kwds)
                    return redirect(login_url)
                if request.user.is_authenticated:
                    return redirect(redirect_url)
                return view(request, *args, **kwds)

        return inner

    return wrapper


class Request:
    @staticmethod
    def _capture_event(
        request: HttpRequest,
        event_name: str,
        callback=lambda *args, **kwargs: (args, kwargs),
    ):
        print(f"Trying to capture event [{event_name}]")
        if request.headers.get("x-events", request.headers.get("X-Events")):
            args, kwargs = arg_parser(
                request.headers.get("x-events", request.headers.get("X-Events"))
            )
            if event_name in args:
                print("Found in headers.")
                return callback(*args, **kwargs)
        elif event_name.lower() in ["post", "get", "head", "put", "delete"]:
            print("Not found in headers.")
            method = getattr(request, event_name.upper(), {})
            if method:
                print("Found in request methods.")
                return callback(event_name.upper(), **method)
        elif event_name.lower() in ["ajax", "x-ajax"]:
            print("Not found in request methods.")
            if request.isAjax:
                print("Found in isAjax.")
                return callback(
                    "X-AJAX", **{"method": request.method, "path": request.path}
                )
            print("Not found in isAjax.")
        print("Could not capture event.")
        return False

    @staticmethod
    def on(
        request_event: typing.AnyStr,
        handler_function: typing.Callable[..., HttpRequest],
    ):
        def bind(view_func):
            sig1 = signature(view_func)
            sig2 = signature(handler_function)
            if "self" in sig1.parameters:
                @wraps(view_func)
                def function(self, request, *args, **kwargs):
                    capture = Request._capture_event(request, request_event)
                    if capture:
                        if "self" in signature(handler_function).parameters:
                            if 'xevent' in sig2.parameters and 'xargs' in sig2.parameters:
                                return handler_function(self, request, *args, xevent=capture[0], xargs=capture[1], **kwargs)
                        return handler_function(self, request, *args, **kwargs)
                    return view_func(self, request, *args, **kwargs)

            else:
                def function(request, *args, **kwargs):
                    capture = Request._capture_event(request, request_event)
                    if capture:
                        if 'xevent' in sig2.parameters and 'xargs' in sig2.parameters:
                            return handler_function(request, *args, xevent=capture[0], xargs=capture[1], **kwargs)
                        return handler_function(request, *args, **kwargs)
                    return view_func(request, *args, **kwargs)

            return function

        return bind

    @staticmethod
    def fake(**options):
        options = (
            dict(
                path="/",
                user=Random.random(User),
                isAjax=Random.BooleanField(),
                headers={
                    "X-Events": "update:user-details??locale=en-us&&name=John Doe"
                },
            )
            | options
        )

        instance = HttpRequest()
        for k, v in options.items():
            setattr(instance, k, v)
        return instance

    @staticmethod
    def bind(request_event, handler_function):
        """
        Bind a callable to an xevent
        on(<xevent>) callable is called

        callable must accept the following parameters
        :param request (an HTTPRequest object that holds the xevent)
        :param xevent (name of the event)
        :param xargs (a dictionary containing arguments of the event)

        example
        =======
        def edit_user_settings(request, xevent, xargs):
            import json
            user = request.user
            if user.is_authenticated:
                old_settings = json.dumps(user.settings)
                new_settings = xargs
                updated_settings = old_settings.update(new_settings)
                user.settings = json.loads(updated_settings)

        bind('edit:user-settings', edit_user_settings)

        Note: you must assign this only once!

        """
        cached_obj = CachedObject(
            "request_handlers", cache=dbcache, version=1, timeout=None
        )
        handlers = cached_obj.get([])
        handlers.append((request_event, handler_function))
        cached_obj.set(handlers, timeout=None)
        return cached_obj

    @staticmethod
    def restrict(allowed_methods=("POST", "GET")):
        def binder(view_func):
            if "self" in signature(view_func).parameters:

                @wraps(view_func)
                def wrapper_func(self, request, *args, **kwargs):
                    context = dict(
                        name="403", reason=f"{request.method} Requests Not Allowed"
                    )
                    if isinstance(allowed_methods, str):
                        if request.method != allowed_methods:
                            return error(request, context, status=403)
                    else:
                        if request.method not in allowed_methods:
                            return error(request, context, status=403)
                    return view_func(self, request, *args, **kwargs)

            else:

                @wraps(view_func)
                def wrapper_func(request, *args, **kwargs):
                    context = dict(
                        name="403", reason=f"{request.method} Requests Not Allowed"
                    )
                    if isinstance(allowed_methods, str):
                        if request.method != allowed_methods:
                            return error(request, context,status=403)
                    else:
                        if request.method not in allowed_methods:
                            return error(request, context, status=403)
                    return view_func(request, *args, **kwargs)

            return wrapper_func

        return binder

    @staticmethod
    def ajax(ajax=False, view_func=None):
        """
        set ajax to True if this view only accepts ajax requests
        if a non-ajax request is sent:
            a 404 error is thrown if view_func is None
            else the view_func is called with all arguments
        set ajax to false if this view doesn't accepts ajax request
        if an ajax request is sent:
            a 404 error is thrown if view_func is None
            else the view_func is called with all arguments
        """

        def default_error(request, reason=""):
            context = dict(name="403", reason=reason or "Ajax Not Allowed Here.")
            return error(request, context, status=403)

        def binder(view):
            if "self" in signature(view).parameters:

                @wraps(view)
                def wrapper_func(self, request, *args, **kwargs):
                    if request.isAjax:
                        if ajax is True:
                            return view(self, request, *args, **kwargs)
                        else:
                            if view_func:
                                if "self" in signature(view_func).parameters:
                                    return view_func(self, request, *args, **kwargs)
                                return view_func(request, *args, **kwargs)
                            else:
                                return default_error(request)
                    else:
                        if ajax is False:
                            return view(self, request, *args, **kwargs)
                        else:
                            if view_func:
                                if "self" in signature(view_func).parameters:
                                    return view_func(self, request, *args, **kwargs)
                                return view_func(request, *args, **kwargs)
                            else:
                                return default_error(
                                    request, "Only Ajax Request Allowed Here."
                                )

            else:

                def wrapper_func(request, *args, **kwargs):
                    if request.isAjax:
                        if ajax is True:
                            return view(request, *args, **kwargs)
                        else:
                            if view_func:
                                return view_func(request, *args, **kwargs)
                            else:
                                return default_error(request)
                    else:
                        if ajax is False:
                            return view(request, *args, **kwargs)
                        else:
                            if view_func:
                                return view_func(request, *args, **kwargs)
                            else:
                                return default_error(
                                    request, "Only Ajax Request Allowed Here."
                                )

            return wrapper_func

        return binder
