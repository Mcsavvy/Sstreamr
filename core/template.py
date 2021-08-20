from django.shortcuts import render
import sys
import traceback
import re
from .caching import CachedObject, dbcache
from time import perf_counter


CachedObject.DEFAULT['cache'] = dbcache


class Builtin:
    settings = dict(
        cache=True,
        timeout=0,
        version=1,
        resolve_dict=True,
        resolve_function=True,
        ajax=None,
        redirect=None,
    )

    def __init__(self, **kwargs):
        self.VARS = []
        self.request = {}

    def register(self, name="var", **settings):
        def register(obj):
            self.VARS.append((name, obj, settings))
            return obj
        return register

    def __call__(self, request):
        # print(
        #     'Updating default context for '
        #     f'{request.user}:{request.method}:{request.path}'
        # )
        # start = perf_counter()
        vars = {}
        for name, var, settings in self.VARS:
            name = name.format(request=request)
            settings = self.settings | settings
            if request.isAjax:
                if settings['ajax'] is False:
                    continue
            else:
                if settings['ajax'] is True:
                    continue
            if re.search('redirect', request.path):
                if settings['redirect'] is False:
                    continue
            else:
                if settings['redirect'] is True:
                    continue
            if callable(var):
                if not settings['resolve_function']:
                    vars[name] = CachedObject(name).get(
                        default=var,
                        timeout=settings['timeout'],
                        version=settings['version']
                    )
                    continue
                result = var(request)
                if isinstance(result, dict) and settings['resolve_dict']:
                    for k in result:
                        k = k.format(request=request)
                        if settings['cache']:
                            vars[k] = CachedObject(k).get(
                                result[k],
                                timeout=settings["timeout"],
                                version=settings['version']
                            )
                    continue
                vars[name] = CachedObject(name).get(
                    result,
                    timeout=settings['timeout'],
                    version=settings['version']
                )
                continue
            if isinstance(var, dict) and settings['resolve_dict']:
                for k in var:
                    k = k.format(request=request)
                    if settings['cache']:
                        vars[k] = CachedObject(k).get(
                            var[k],
                            timeout=settings["timeout"],
                            version=settings['version']
                        )
                continue
            else:
                vars[name] = CachedObject(name).get(
                    var,
                    timeout=settings["timeout"],
                    version=settings['version']
                )
        # print(
        #     f'Updating took {perf_counter() - start:0.4f} seconds'
        # )
        # print(
        #     f'All context variables {tuple(vars)}'
        # )
        return vars


builtins = Builtin()


def render_error(request, context=None, content_type=None, status=None, using=None):
    from .builtins import builtins as BUILTINS
    context = context or {}
    context.update(BUILTINS(request))
    return render(
        request, 'errors/generic.html',
        context, content_type=content_type,
        status=status, using=using
    )


def error(request, err=None, **extra):
    """Only use this in an exception"""
    from .builtins import builtins as BUILTINS
    BUILTINS.request['error'] = True
    context = dict(
        name="404",
        thrown=err.__class__.__name__,
        reason=err.args[0],
        tracebacks=traceback.format_tb(err.__traceback__)
    )
    context.update(BUILTINS(request))
    context.update(extra)
    return render_error(request, context, status=404)


def render_template(
    request, template_name,
    context=None, content_type=None,
    status=None, using=None, debug=False
):
    context = context or {}
    from .builtins import builtins as BUILTINS
    if debug or ("no-err" in request.GET):
        context.update(BUILTINS(request))
        return render(request, template_name, context)
    try:
        context.update(BUILTINS(request))
        data = render(request, builtins.request.get('template', template_name), context)
        return data
    except Exception as err:
        BUILTINS.request['error'] = True
        return error(request, err)
