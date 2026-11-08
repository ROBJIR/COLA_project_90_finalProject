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

"""
class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = "showcase_auth/profile.html"
    
"""
class UserProfile(View):
    def __init__(self):
        self.webpageattributes = {
                  "application_code": "cassiopeia"
                , "application_name": "Cassiopeia Projects"
                , "module_code": "userprofile"
                , "module_template": "auth/user-profile.html"
                , "module_name": "User Profile"}
        self.webdata = {}
    def get(self, request):
        if request.user.is_authenticated:
            return WebMachine.web_renderer(self, request, self.webpageattributes, self.webdata)
        else:
            return redirect("login")

class UserLogin(View):
    def __init__(self):
        self.webpageattributes = {
                  "application_code": "cassiopeia"
                , "application_name": "Cassiopeia Projects"
                , "module_code": "userlogin"
                , "module_template": "auth/user-login.html"
                , "module_name": "Login"}
        self.webdata = {}
    def get(self, request):
        return WebMachine.web_renderer(self, request, self.webpageattributes, self.webdata)
    def post(self, request):
        user = authenticate(request, username=request.POST.get("username"), password=request.POST.get("password"))
        if user is not None:
            login(request, user)
            return redirect("userprofile")
        else:
            WebMachine.sys_message_set(request, "alert-danger", "Incorrect username or password!")
            return WebMachine.web_renderer(self, request, self.webpageattributes, self.webdata)

class UserLogout(View):
    def get(self, request):
        logout(request)
        WebMachine.sys_message_set(request, "alert-success", "User has been successfully logged out.")
        return redirect("home")

class UserPasswordChange(LoginRequiredMixin, View):
    def get(self, request):
        self.webpageattributes = {
                  "application_code": "cassiopeia"
                , "application_name": "Cassiopeia Projects"
                , "module_code": "userprofile"
                , "module_template": "auth/user-profile.html"
                , "module_name": "User Profile"}
        self.webdata = {"profile_action": "change_password"}
        return WebMachine.web_renderer(self, request, self.webpageattributes, self.webdata)
    def post(self, request):
        self.webpageattributes = {
                  "application_code": "cassiopeia"
                , "application_name": "Cassiopeia Projects"
                , "module_code": "userprofile"
                , "module_template": "auth/user-profile.html"
                , "module_name": "User Profile"}
        self.webdata = {}
        form = request.POST
        if form:
            oldpassword = form["oldpassword"]

            if not request.user.check_password(oldpassword):
                self.webdata = {"profile_action": "change_password"}
                WebMachine.sys_message_set(request, "alert-danger", "Incorrect OLD password!")
                return WebMachine.web_renderer(self, request, self.webpageattributes, self.webdata)

            if form["newpassword1"] == form["newpassword2"]:
                request.user.set_password(form["newpassword1"])
                request.user.save()
                update_session_auth_hash(request, request.user)
                WebMachine.sys_message_set(request, "alert-success", "Password has been successfully changed.")
                return WebMachine.web_renderer(self, request, self.webpageattributes, self.webdata)
            else:
                self.webdata = {"profile_action": "change_password"}
                WebMachine.sys_message_set(request, "alert-danger", "Passwords do not match!")
                return WebMachine.web_renderer(self, request, self.webpageattributes, self.webdata)


