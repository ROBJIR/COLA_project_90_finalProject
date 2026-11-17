import logging

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib.auth import update_session_auth_hash
from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.models import Group
from django.db import transaction
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import authenticate, login, logout
from .web import WebMachine
from syslog.views.logging import SysLogging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Permission
from django.contrib.auth.decorators import permission_required

logger = logging.getLogger("cassiopeia.auth")

class UserProfile(View):
    def __init__(self):
        self.web_data = {}
    def get(self, request):
        if request.user.is_authenticated:
            return WebMachine.web_renderer(self, request, 'userprofile', self.web_data)
        else:
            return redirect("login")

class UserRegistration(View):
    def __init__(self):
        self.web_data = {}
    def get(self, request):
        if request.user.is_authenticated:
            return WebMachine.web_renderer(self, request, 'userprofile', self.web_data)
        else:
            self.web_data = {'registration_step':'(step 1/2)'}
            return WebMachine.web_renderer(self, request, 'userregistration', self.web_data)

    def post(self, request):
        if request.user.is_authenticated:
            return WebMachine.web_renderer(self, request, 'userprofile', self.web_data)
        else:
            if request.POST.get("registration_step") == '(step 1/2)':
                form = UserCreationForm(data={
                    "username": request.POST.get("username", "").lower(),
                    "password1": request.POST.get("password", ""),
                    "password2": request.POST.get("password-again", ""),
                })
                if form.is_valid():
                    user = form.save()  # Vytvoří uživatele s hashovaným heslem.
                    request.session["registration_user_id"] = user.pk
                    msg = f"User <strong>{user}</strong> was successfully created."
                    SysLogging.log(
                        request,
                        alert_code='success',
                        webmessage_show='auth',
                        module_code='UserRegistration',
                        action_code='registration',
                        step_code=None,
                        status_code='success',
                        parameters_value={},
                        retval_value=user,
                        error_code=None,
                        error_message=None,
                        webmessage_body=msg)
                    self.web_data = {'registration_step': '(step 2/2)'}
                    return WebMachine.web_renderer(self, request, 'userregistration', self.web_data)

                SysLogging.log(
                    request,
                    alert_code='danger',
                    webmessage_show='auth',
                    module_code='UserRegistration',
                    action_code='registration',
                    step_code=None,
                    status_code='error',
                    parameters_value={},
                    retval_value='',
                    error_code=None,
                    error_message=None,
                    webmessage_body=''.join(error for errors in form.errors.values()
                                                  for error in errors)
                )
                self.web_data = {'registration_step': '(step 1/2)'}
                return WebMachine.web_renderer(self, request, 'userregistration', self.web_data)


            if request.POST.get("registration_step") == '(step 2/2)':
                form = request.POST
                with transaction.atomic():
                    user_id = request.session["registration_user_id"]
                    request.session.pop("registration_user_id", None)

                    user = User.objects.get(pk=user_id)
                    user.first_name = request.POST.get("first_name", "").strip()
                    user.last_name = request.POST.get("last_name", "").strip()
                    user.email = request.POST.get("email", "").strip()
                    user.save()
                    public_group = Group.objects.get(name="public")
                    user.groups.add(public_group)

                SysLogging.log(
                    request,
                    alert_code='success',
                    webmessage_show='web',
                    module_code='UserRegistration',
                    action_code='saveUserDetail',
                    step_code=None,
                    status_code='success',
                    parameters_value={},
                    retval_value='',
                    error_code=None,
                    error_message=None,
                    webmessage_body='User saved successfully. Now you have to log in!'
                )
                return WebMachine.web_renderer(self, request, 'userlogin', self.web_data)


class UserLogin(View):
    def __init__(self):
        self.web_data = {}
    def get(self, request):
        return WebMachine.web_renderer(self, request, 'userlogin', self.web_data)
    def post(self, request):
        user = authenticate(request, username=request.POST.get("username").lower(), password=request.POST.get("password"))
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

            return WebMachine.web_renderer(self, request, 'userLogin', self.web_data)

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
                new_password = form["newpassword1"]

                try:
                    validate_password(new_password, user=request.user)
                except ValidationError as error:
                    self.webdata = {"profile_action": "change_password"}

                    SysLogging.log(
                        request,
                        alert_code="danger",
                        webmessage_show="auth",
                        module_code="userprofile",
                        action_code="change_password",
                        step_code=None,
                        status_code="error",
                        parameters_value={"username": request.user.username},
                        retval_value=request.user.username,
                        error_message=" ".join(error.messages),
                    )

                    return WebMachine.web_renderer(
                        self, request, "userprofile", self.webdata
                    )

                request.user.set_password(new_password)
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


