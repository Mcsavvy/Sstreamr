import hashlib
from .main import *


def make_key(key, key_prefix, version):
    str2hash = key
    result = hashlib.md5(str2hash.encode())
    return '%s:%s:%s' % (key_prefix, version, result.hexdigest())


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'wn^nj1$&*7t^=n*@c=jj%c@($*9+j##*)gj!9k8l_2^v*b+ou6'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# Caches
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        'LOCATION': '127.0.0.1:11211',
    },
    'memcache': {
        "BACKEND": 'django.core.cache.backends.memcached.PyMemcacheCache',
        "LOCATION": '0.0.0.0:11211',
        "KEY_PREFIX": "memcache",
        "VERSION": 1,
        "KEY_FUNCTION": make_key,
        "TIMEOUT": 60,

    },
    'dbcache': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'db_caching',
        "KEY_PREFIX": "dbcache",
        "VERSION": 1,
        "KEY_FUNCTION": make_key,
        "TIMEOUT": 6.307e+7,
    },
    'filecache': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': '/var/tmp/file_caching',
        "KEY_PREFIX": "filecache",
        "VERSION": 1,
        "KEY_FUNCTION": make_key,
        "TIMEOUT": 60,
    }
}

USER_AGENTS_CACHE = "default"

LOGIN_REDIRECT_URL = "/auth/redirect///"

YOUTUBE_DATA_API_KEY = 'AIzaSyAEmt2jvu4d5vlYVKFoEpL_r_v42iWVtxw'

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

IGAUTH = 'hood@ins.com'

