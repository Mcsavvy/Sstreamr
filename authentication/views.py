from core import render
from django.views.generic import View
from django.shortcuts import redirect
from core.models import User, Node, nodify
from core.utils import arg_parser
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.utils import timezone
from django.core import serializers
from core.decorators import Request, authenticated_user
from django.http import JsonResponse
from bug import Bug
from django_user_agents.utils import get_user_agent
import re

# Create your views here.


class XEvents(View):

    def edit_profile(self, request, xevent=None, xargs=None):
        default = JsonResponse({})
        this = request.user
        node = this.node
        if not this.is_authenticated:
            return default
        username, email, password = tuple(map(
            lambda key: xargs.get(key, '').strip(),
            'username email password'.split()
        ))
        srnm = ml = pwd = False
        if username and not Main.validate_username(request, username):
            srnm = True
        if password and not Main.validate_password(request, password):
            pwd = True
        if ml and not not Create.validate_email(request, email):
            ml = True
        if any((srnm, ml, pwd)):
            node.notify(
                'Unsuccessful attempt to change profile information.', 'warning'
            )
            return JsonResponse({
                'message':
                    f'We could not validate the information you provided??title=Hey {this.username}&&type=error'
            })
        if username and this.username != username:
            this.username = username
        if email and this.email != email:
            this.email = email
        if password:
            this.set_password(password)
        this.save()
        login(request, this)
        node.notify(
            'You updated your profile successfully', 'success'
        )
        return JsonResponse(
            {
                'message': f'Your profile has been updated??title=Hey {this.username}&&type=success'
            }
        )

    @Request.on("edit:profile", edit_profile)
    def get(self, request):
        return JsonResponse({})

    @Request.restrict(allowed_methods=['GET'])
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class Main(View):
    def ajax(self, request):
        return JsonResponse(
            {"message": "Ajax requests not allowed.", "level": "warning"}
        )
    
    @authenticated_user(False)
    @Request.ajax(False, view_func=ajax)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    @authenticated_user(False, login_url="/auth/redirect//auth/")
    def get(self, request):
        return render(request, "auth/main.html")

    @staticmethod
    def validate_username(request, username):
        long, short, bad_chars, good_chars = "", "", "", ""
        if len(username) < 3:
            short = "<li class=px-15>Username must be three characters or more</li>"
        elif len(username) > 25:
            long = "<li class=px-15>Username too long, use 25 characters or less</li>"
        if not re.match("^((?![^a-zA-Z0-9_]).)*$", username):
            bad_chars = "<li class=px-15>Username can only contain letters, numbers & underscores</li>"
        if not re.match("[a-zA-Z0-9]", username):
            good_chars = "<li class=px-15>Username cannot contain only underscores</li>"
        if any((long, short, bad_chars, good_chars)):
            messages.error(
                request,
                "<ul>{}{}{}{}</ul>??title=Rectify the following".format(
                    long, short, bad_chars, good_chars
                ),
            )
            return False
        return True

    @staticmethod
    def validate_password(request, password):
        if len(password) < 6:
            messages.error(
                request,
                "Use a more secure password of at least 6 characters??title=Password too short.",
            )
            return False
        return True

    def post(self, request):
        username = request.POST["username"].strip()
        password = request.POST["password"].strip()
        if not self.validate_username(request, username):
            self.validate_password(request, password)
            return redirect("/auth/redirect//auth/")
        if not self.validate_password(request, password):
            return redirect("/auth/redirect//auth/")
        request.session["username"] = username
        request.session["password"] = password
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return redirect("/auth/redirect//auth/join")
        nodify(user)
        if authenticate(request, username=username, password=password):
            request.session["user"] = serializers.serialize("json", [user])
            return redirect("/auth/redirect//auth/login")
        else:
            messages.error(
                request, "We could not authenticate you..??title=Invalid Credentials"
            )
            return self.authentify(request, redirect("auth.main"))

    def authentify(self, request, response):
        if "retries" not in request.session:
            request.session["retries"] = 0

        request.session["retries"] += 1
        if request.session["retries"] in [3, 5]:
            messages.info(request, "We can't seem to find your account.??title=Oopsie")
        elif request.session["retries"] in [4, 6]:
            messages.info(request, "try recovering your account.??title=Why not..")
        elif request.session["retries"] in [2, 8]:
            messages.info(request, "try to type more slowly.??title=We suggest you..")
        elif request.session["retries"] >= 10:
            messages.info(request, "Try to type more slowly.??title=We suggest you..")
            return redirect("/auth/redirect//auth")
        return response


class Create(View):
    def get(self, request):
        if not request.session.get("username"):
            return redirect("/auth/redirect//auth")
        context = {}
        return render(request, "auth/create.html", context=context)

    @Request.ajax(False)
    @authenticated_user(False)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    @staticmethod
    def validate_email(request, email):
        if not re.match(r"^(\w|(\.(?!\.)))+@([\w-]+\.)+[\w-]{2,4}$", email):
            messages.error(
                request,
                "Try retyping it carefully <i>avoid using spaces</i>??title=That was not an email",
            )
            return False
        return True

    def post(self, request):
        if not self.validate_email(request, request.POST["email"].strip()):
            return redirect("/auth/redirect//auth/join")
        if request.session["password"] != request.POST["password"].strip():
            messages.error(
                request, "Passwords did not match.??title=Use forgot password"
            )
            return redirect("/auth/redirect//auth/join")
        try:
            user = User.objects.get(username=request.session["username"])
            messages.warning(
                request, f"That username is no longer available.??title=Yo!"
            )
            del request.session["username"]
            del request.session["password"]
            return redirect("/auth/redirect//auth/join")
        except User.DoesNotExist:
            user = User.objects.create(
                username=request.session["username"],
                email=request.POST["email"].strip(),
            )
            user.set_password(request.POST["password"].strip())
            nodify(user)
            user.node.notify(
                'Welcome to unlimited Sstreaming. Feel free to indulge your senses<i class=\'fas fa-heart pm\'></i>'
            )
            user.node.notify(
                'Ssteamr works best if you have an instagram account.'
            )
            user.node.notify(
                'You can add one by clicking the floating action button at the bottom right part of your screen'
            )
            messages.success(
                request,
                f"{user.username}, you are now one of our streamrs.??title=YaY!",
            )
            messages.info(
                request, f"We'll be with you shortly...??title=Take your time"
            )
            login(request, user)
            del request.session["username"]
            del request.session["password"]
            return redirect("/auth/redirect///")


class Login(View):
    def get(self, request):
        if not request.session.get("username"):
            return redirect("/auth/redirect//auth")
        username, password = request.session["username"], request.session["password"]
        if not (username and password):
            messages.error(request, "An error occurred!??It's on us.")
            del request.session["username"]
            del request.session["password"]
            return redirect("/auth/redirect//auth")
        user = authenticate(request, username=username, password=password)
        if not user:
            messages.error(
                request, "we could not validate your credentials.??title=Sorry"
            )
            del request.session["username"]
            del request.session["password"]
            return redirect("/auth/redirect//auth")
        login(request, user)
        messages.info(
            request,
            f"let us show you what you missed..??title=Welcome back {username}!",
        )
        return redirect("/auth/redirect///")

    @authenticated_user(False)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class Logout(View):
    def get(self, request):
        logout(request)
        messages.info(
            request,
            f"{request.user.username}, you have been logged out.??title=We'll see you soon",
        )
        return redirect("/auth/redirect//auth")

    @authenticated_user(True)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class Redirect(View):
    def non_ajax_post(self, request, *args, **kwargs):
        return JsonResponse(
            {"message": "Message could not be understood", "level": "error"}
        )

    def do_redirect(self, request, *args, **kwargs):
        print(args, kwargs, sep="??")
        return JsonResponse({"url": kwargs["path"]})

    @Request.on("do:redirect", do_redirect)
    def get(self, request, path):
        return render(request, "auth/redirect.html")

    @Request.ajax(True, view_func=non_ajax_post)
    def post(self, request):
        return JsonResponse({})


class Blank(View):
    reasons = {"mobile-restrict": "This site is exclusively for mobile viewing"}

    def get(self, request, reason):
        after = request.GET.get("after", "/")
        print("re")
        return render(
            request,
            "auth/blank.html",
            dict(message=self.reasons.get(reason, ""), after=after),
        )
