from django.http.response import HttpResponse
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import TemplateView
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from syscor.views.tools import sysTools
import datetime
from sysadm.views.base import SysInfoBase
from syscor.views.web import WebMachine

class SysAdmView(View):
    def __init__(self):
        self.web_data = {}
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
        return WebMachine.web_renderer(self, request, 'sysadm', self.web_data)

class SessionsInfoView(View):
    def __init__(self):
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
            'sessionsinfo',
            self.web_data,
        )

class CookiesInfoView(View):
    def __init__(self):
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
            'cookieinfo',
            self.web_data,
        )

class SysInfoUserList(View):
    def __init__(self):
        self.web_data = {}
    def get(self, request):
        users = User.objects.all().values()
        # print(WebMachine.html_table_generator(users))
        self.web_data={"users":users}
        return WebMachine.web_renderer(self, request, 'sysadm-userlist', self.web_data)

