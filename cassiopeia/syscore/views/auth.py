from django.shortcuts import render
from django.views import View
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from .web import WebMachine

class sysLogin(View):
    def __init__(self):
        self.webpageattributes = {
                  "application_code": "cassiopeia"
                , "application_name": "Cassiopeia Projects"
                , "module_code": "syslogin"
                , "module_template": "core-syslogin.html"
                , "module_name": "Login"}
        self.webdata = {}
    def get(self, request):
        return WebMachine.web_renderer(self, request, self.webpageattributes, self.webdata)
    def post(self, request):
        user = authenticate(request, username=request.POST.get("username"), password=request.POST.get("password"))
        login(request, user)
        return WebMachine.web_renderer(self, request, self.webpageattributes, self.webdata)

class sysLogout(View):
    def __init__(self):
        self.webpageattributes = {
                  "application_code": "cassiopeia"
                , "application_name": "Cassiopeia Projects"
                , "module_code": "syslogin"
                , "module_template": "core-syslogin.html"
                , "module_name": "Logout"}
        self.webdata = {}
    def get(self, request):
        logout(request)
        return WebMachine.web_renderer(self, request, self.webpageattributes, self.webdata)

class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = "showcase_auth/profile.html"