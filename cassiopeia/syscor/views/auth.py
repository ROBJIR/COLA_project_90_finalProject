import logging

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
from syslog.views.logging import SysLogging

logger = logging.getLogger("cassiopeia.auth")

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
            logger.info("Logged user %r.", user.get_username())

            SysLogging.log(
                request,
                alert_code='info',
                webmessage_show=None,
                module_code='userLogin',
                action_code='login',
                step_code=request.user.username,
                status_code='success',
                parameters_value={"username":request.user.username},
                retval_value=request.user.username,
            )

            return redirect("profile")
        else:
            logger.warning("Failed login attempt for username %r.",request.POST.get("username"),
            )
            SysLogging.log(
                request,
                alert_code='danger',
                webmessage_show='auth',
                module_code='userLogin',
                action_code='login',
                step_code=None,
                status_code='error',
                parameters_value={"username":request.POST.get("username")},
                retval_value=request.POST.get("username"),
                error_code='error-2010',
                error_message='Incorrect username or password!',
            )

            return WebMachine.web_renderer(self, request, 'userLogin', self.webdata)

class UserLogout(View):
    def get(self, request):
        loged_username=request.user.username
        logout(request)

        logger.info("Loggout user %r.", loged_username)

        SysLogging.log(
            request,
            alert_code='success',
            webmessage_show='web',
            module_code='userLogout',
            action_code='logout',
            step_code=None,
            status_code='success',
            parameters_value={'username':loged_username},
            retval_value=loged_username,
            error_code=None,
            error_message=None,
            webmessage_body='User has been successfully logged out.',
        )

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

                SysLogging.log(
                    request,
                    alert_code='danger',
                    webmessage_show='auth',
                    module_code='userprofile',
                    action_code='change_password',
                    step_code=None,
                    status_code='error',
                    parameters_value={"username": request.user.username},
                    retval_value=request.user.username,
                    error_code='error-2011',
                    error_message='Incorrect OLD password!',
                )

                return WebMachine.web_renderer(self, request, 'userprofile', self.webdata)

            if form["newpassword1"] == form["newpassword2"]:
                request.user.set_password(form["newpassword1"])
                request.user.save()
                update_session_auth_hash(request, request.user)

                SysLogging.log(
                    request,
                    alert_code='success',
                    webmessage_show='auth',
                    module_code='userprofile',
                    action_code='change_password',
                    step_code=None,
                    status_code='success',
                    parameters_value={"username": request.user.username},
                    retval_value=request.user.username,
                    error_code=None,
                    error_message=None,
                    webmessage_body='Password has been successfully changed.',
                )

                return WebMachine.web_renderer(self, request, 'userprofile', self.webdata)
            else:
                self.webdata = {"profile_action": "change_password"}

                SysLogging.log(
                    request,
                    alert_code='danger',
                    webmessage_show='auth',
                    module_code='userprofile',
                    action_code='change_password',
                    step_code=None,
                    status_code='error',
                    parameters_value={"username": request.user.username},
                    retval_value=request.user.username,
                    error_code='error-2012',
                    error_message='Passwords do not match!',
                )

                return WebMachine.web_renderer(self, request, 'userprofile', self.webdata)


