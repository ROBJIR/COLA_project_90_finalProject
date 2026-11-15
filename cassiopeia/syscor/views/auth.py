from django.shortcuts import render, redirect
from django.views import View
from django.http import HttpResponse
from django.contrib.auth import update_session_auth_hash
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Permission
from django.contrib.auth.decorators import permission_required
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from .web import WebMachine
from syslog.views.syslog import SysLogging


class UserProfile(View):
    def __init__(self):
        self.webdata = {}
    def get(self, request):
        if request.user.is_authenticated:
            return WebMachine.web_renderer(self, request, 'userprofile', self.webdata)
        else:
            return redirect("login")

class UserLogin(View):
    def __init__(self):
        self.webdata = {}
    def get(self, request):
        return WebMachine.web_renderer(self, request, 'userlogin', self.webdata)
    def post(self, request):
        user = authenticate(request, username=request.POST.get("username"), password=request.POST.get("password"))
        if user is not None:
            login(request, user)

            SysLogging.log(request, 'info',None,  'userLogin', 'login'
                                    , request.user.username, 'success'
                                    , {"username":request.user.username,"password":request.POST.get("password")}
                                    , request.user.username)

            return redirect("profile")
        else:
            SysLogging.log(request, 'danger', 'auth', 'userLogin', 'login'
                                    , request.POST.get("username"), 'error'
                                    , {"username":request.POST.get("username"),"password":request.POST.get("password")}
                                    , request.POST.get("username"), 'error-2010', 'Incorrect username or password!')

            return WebMachine.web_renderer(self, request, 'userLogin', self.webdata)

class UserLogout(View):
    def get(self, request):
        loged_username=request.user.username
        logout(request)
        SysLogging.log(request, 'success', 'web', 'userLogout', 'logout'
                       , loged_username, 'success'
                       , {'username':loged_username}
                       , loged_username, None, None,'User has been successfully logged out.')

        return redirect("home")

class UserPasswordChange(LoginRequiredMixin, View):
    def get(self, request):
        self.webdata = {"profile_action": "change_password"}
        return WebMachine.web_renderer(self, request, 'userprofile', self.webdata)
    def post(self, request):
        self.webdata = {}
        form = request.POST
        if form:
            oldpassword = form["oldpassword"]

            if not request.user.check_password(oldpassword):
                self.webdata = {"profile_action": "change_password"}

                SysLogging.log(request, 'danger', 'auth', 'userprofile', 'change_password'
                               , request.user.username, 'error'
                               , {"username": request.user.username, "oldpassword": oldpassword}
                               , request.user.username, 'error-2011', 'Incorrect OLD password!')

                return WebMachine.web_renderer(self, request, 'userprofile', self.webdata)

            if form["newpassword1"] == form["newpassword2"]:
                request.user.set_password(form["newpassword1"])
                request.user.save()
                update_session_auth_hash(request, request.user)

                SysLogging.log(request, 'success', 'auth', 'userprofile', 'change_password'
                               , request.user.username, 'success'
                               , {"username": request.user.username, "newpassword": form["newpassword1"]}
                               , request.user.username, None, None, 'Password has been successfully changed.')

                return WebMachine.web_renderer(self, request, 'userprofile', self.webdata)
            else:
                self.webdata = {"profile_action": "change_password"}

                SysLogging.log(request, 'danger', 'auth', 'userprofile', 'change_password'
                               , request.user.username, 'error'
                               , {"username": request.user.username, "newpassword1": form["newpassword1"], "newpassword2": form["newpassword2"]}
                               , request.user.username, 'error-2012', 'Passwords do not match!')

                return WebMachine.web_renderer(self, request, 'userprofile', self.webdata)


