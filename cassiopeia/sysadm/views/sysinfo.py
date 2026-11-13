from django.http.response import HttpResponse
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import TemplateView
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from syscore.views.tools import sysTools
import datetime
from sysadm.views.base import SysInfoBase
from syscore.views.web import WebMachine

class SysInfoView(View):
    def __init__(self):
        self.web_page_attributes = {
              "application_code": "sysadm"
            , "application_name": "System Administrations"
            , "module_code":      "sysinfo"
            , "module_template":  "sysinfo.html"
            , "module_name":      "System Administrations"}
        self.web_data = {"webmain":""}
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
        self.web_data["webmain"] = webmain
        return WebMachine.web_renderer(self, request, self.web_page_attributes, self.web_data)

class SessionsInfoView(View):
    def __init__(self):
        self.web_page_attributes = {
              "application_code": "sysadm"
            , "application_name": "System Administrations"
            , "module_code":      "sessionsinfo"
            , "module_template":  "sysinfo-sesscookielist.html"
            , "module_name":      "Sessions Info"}
        self.web_data = {}
    def get(self,request):
        sessions = dict(request.session.items())
        data = sysTools.dictionary_to_data(sessions)
        self.web_data = {
            "html_table": WebMachine.dictionary_to_html_table(data),
        }
        return WebMachine.web_renderer(
            self,
            request,
            self.web_page_attributes,
            self.web_data,
        )

class CookiesInfoView(View):
    def __init__(self):
        self.web_page_attributes = {
              "application_code": "sysadm"
            , "application_name": "System Administrations"
            , "module_code":      "cookieinfo"
            , "module_template":  "sysinfo-sesscookielist.html"
            , "module_name":      "Cookie Info"}
        self.web_data = {}
    def get(self,request):
        cookies = dict(request.COOKIES.items())
        data = sysTools.dictionary_to_data(cookies)
        self.web_data = {
            "html_table": WebMachine.dictionary_to_html_table(data),
        }
        return WebMachine.web_renderer(
            self,
            request,
            self.web_page_attributes,
            self.web_data,
        )

class SysInfoUserList(View):
    def __init__(self):
        self.web_page_attributes = {
              "application_code": "sysadm"
            , "application_name": "System Administrations"
            , "module_code":      "sysinfo-userlist"
            , "module_template":  "sysinfo-userlist.html"
            , "module_name":      "Admin module: Users"}
        self.web_data = {}
    def get(self, request):
        users = User.objects.all().values()
        # print(WebMachine.html_table_generator(users))
        self.web_data={"users":users}
        return WebMachine.web_renderer(self, request, self.web_page_attributes, self.web_data)

