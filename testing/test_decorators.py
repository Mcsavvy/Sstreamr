from functools import partial
from io import StringIO
import unittest
from django.http.response import JsonResponse, HttpResponse
from django.test import TestCase
from django.contrib.auth.models import AnonymousUser, Group, User
from core import decorators as dec


class TestDecorators(TestCase):
    def setUp(self) -> None:
        self.groups = {
            "customer": Group.objects.create(name="customer"),
            "admin": Group.objects.create(name="admin"),
        }
        self.users = {
            "allowed": User.objects.create(username="allowed"),
            "unallowed": User.objects.create(username="unallowed"),
            "guest": AnonymousUser(),
        }
        self.users["allowed"].groups.add(self.groups["customer"])
        self.users["allowed"].save()
        return super().setUp()

    def test_allowed_user(self):
        @dec.allowed_user(["customer", "admin"])
        def test_view(request):
            return JsonResponse({})

        request = dec.Request.fake(user=self.users["unallowed"])
        response = test_view(request)
        self.assertFalse(isinstance(response, JsonResponse))
        self.assertTrue(response.status_code, 405)
        request = dec.Request.fake(user=self.users["allowed"])
        response = test_view(request)
        self.assertTrue(isinstance(response, JsonResponse))
        self.assertTrue(response.status_code, 200)

    def test_authenticated_user(self):
        @dec.authenticated_user(True, login_url='/auth/')
        def only_authenticated_user(request):
            return JsonResponse({})
        request = dec.Request.fake(user=self.users["guest"])
        response = only_authenticated_user(request)
        self.assertFalse(isinstance(response, JsonResponse))
        self.assertTrue(response.status_code, 302) # redirect
        request = dec.Request.fake(user=self.users["allowed"])
        response = only_authenticated_user(request)
        self.assertTrue(isinstance(response, JsonResponse))
        self.assertTrue(response.status_code, 200)

        @dec.authenticated_user(False, redirect_url="/")
        def only_guests_users(request):
            return JsonResponse({})
        request = dec.Request.fake(user=self.users["guest"])
        response = only_guests_users(request)
        self.assertTrue(isinstance(response, JsonResponse))
        self.assertTrue(response.status_code, 200)
        request = dec.Request.fake(user=self.users["allowed"])
        response = only_guests_users(request)
        self.assertFalse(isinstance(response, JsonResponse))
        self.assertTrue(response.status_code, 302) # redirect


# class TestRequest(unittest.TestCase):
#     def setUp(self) -> None:
#         self.request = dec.Request.fake(
#             isAjax=True
#         )
#         return super().setUp()

#     def test_capture_event(self):
#         io = StringIO()
#         def echo_io(*args, **kwargs):
            


