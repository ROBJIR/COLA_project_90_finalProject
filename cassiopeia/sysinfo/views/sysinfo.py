from django.http.response import HttpResponse
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import TemplateView
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from syscore.views.tools import sysTools
import datetime
from sysinfo.views.base import SysInfoBase
from syscore.views.web import WebMachine

class SysInfoView(View):
    def __init__(self):
        self.webpageattributes = {
              "application_code": "sysinfo"
            , "application_name": "System Informations"
            , "module_code":      "sysinfo"
            , "module_template":  "sysinfo.html"
            , "module_name":      "System Informations"}
        self.webdata = {"webmain":""}
    def timeline(self):
        csdays = ["pondělí", "úterý", "středa", "čtvrtek", "pátek", "sobota", "neděle"]
        currdate = datetime.datetime.now()
        tl = f"today is <strong>{str(currdate.strftime("%A")).lower()}/{csdays[currdate.weekday()]} {str(currdate.date())}</strong>"
        tl = f"{tl}\n<br>\ncurrent time: <strong>{datetime.datetime.now().time().strftime("%H:%M")}</strong>"
        return tl
    def get(self, request):
        webmain = self.timeline()
        system_info = SysInfoBase.SysInfoSystem(self)
        webmain += SysInfoBase.SysInfoToTable(self, system_info)
        self.webdata["webmain"] = webmain
        return WebMachine.web_renderer(self, request, self.webpageattributes, self.webdata)

class SessionsInfoView(View):
    def __init__(self):
        self.webpageattributes = {
              "application_code": "sysinfo"
            , "application_name": "System Informations"
            , "module_code":      "sessionsinfo"
            , "module_template":  "sysinfo-sesscookielist.html"
            , "module_name":      "Sessions Info"}
        self.webdata = {}
    def get(self,request):
        sessions = dict(request.session.items())
        data = sysTools.dictionary_to_data(sessions)
        self.webdata = {
            "html_table": WebMachine.dictionary_to_html_table(data),
        }
        return WebMachine.web_renderer(
            self,
            request,
            self.webpageattributes,
            self.webdata,
        )

class CookiesInfoView(View):
    def __init__(self):
        self.webpageattributes = {
              "application_code": "sysinfo"
            , "application_name": "System Informations"
            , "module_code":      "cookieinfo"
            , "module_template":  "sysinfo-sesscookielist.html"
            , "module_name":      "Cookie Info"}
        self.webdata = {}
    def get(self,request):
        cookies = dict(request.COOKIES.items())
        data = sysTools.dictionary_to_data(cookies)
        self.webdata = {
            "html_table": WebMachine.dictionary_to_html_table(data),
        }
        return WebMachine.web_renderer(
            self,
            request,
            self.webpageattributes,
            self.webdata,
        )

class SysInfoUserList(View):
    def __init__(self):
        self.webpageattributes = {
              "application_code": "sysinfo"
            , "application_name": "System Informations"
            , "module_code":      "sysinfo-userlist"
            , "module_template":  "sysinfo-userlist.html"
            , "module_name":      "Admin module: Users"}
        self.webdata = {}
    def get(self, request):
        users = User.objects.all().values()
        print(WebMachine.html_table_generator(users))
        self.webdata={"users":users ,"chusers":WebMachine.html_table_generator(users)}
        return WebMachine.web_renderer(self, request, self.webpageattributes, self.webdata)
