from django.test import TestCase
from time import sleep
from core.caching import (
    CachedObject,
    dbcache
)

class TestCachedObject(TestCase):
    '''
    A cached object is expected to store a value for a <timeout> seconds
    '''
    def setUp(self) -> None:
        self.object = CachedObject('test', timeout=10, version=1)
        return super().setUp()

    def test__init__(self):
        self.assertEqual(self.object.settings['cache'], dbcache)
        self.assertEqual(self.object.settings['timeout'], 10)
        self.assertEqual(self.object.settings['version'], 1)
        self.assertEqual(self.object._key, 'test')

    def test_get(self):
        self.assertEqual(self.object.get(), None)
        self.assertEqual(self.object.get('test'), 'test')
        # sleep(5)
        self.assertEqual(self.object.get(), 'test')
        # sleep(5)
        # self.assertEqual(self.object.get(), None)