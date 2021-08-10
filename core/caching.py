from django.core.cache import caches
import typing
from inspect import signature, Signature, Parameter

memcache = caches['memcache']
filecache = caches['filecache']
dbcache = caches['dbcache']
default = caches['default']


class CachedObject:
    """
    This represents a single cache object
    The goal is the implement cached object    
    
    """
    DEFAULT = {
        'cache': dbcache
    }

    def __init__(self, key, **settings):
        self.settings = dict(
            cache=self.DEFAULT['cache'],
            version=None,
            timeout=60,
        ) | settings
        self._key = key

    def __repr__(self) -> str:
        s = self.settings
        return f"CachedObject({self._key}, caching_to={s['cache']}, timeout={s['timeout']}, version={s['version']})"

    def set(
        self,
        value,
        **settings
    ):
        settings.get('cache', self.settings['cache']).set(
            self._key, value,
            timeout=settings.get('timeout', self.settings['timeout']),
            version=settings.get('version', self.settings['version'])
        )

    def get(
        self,
        default=None,
        **settings
    ):
        _get = settings.get('cache', self.settings['cache']).get(
            self._key,
            version=settings.get('version', self.settings['version'])
        )
        if _get is None and default is not None:
            self.set(
                default,
                version=settings.get('version', self.settings['version']),
                timeout=settings.get('timeout', self.settings['timeout']),
            )
            return self.settings['cache'].get(
                self._key,
                default,
                version=settings.get('version', self.settings['version']),
            )
        return _get
