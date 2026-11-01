from django.http.response import HttpResponse
from django.shortcuts import render
from django.views import View
from django.views.generic import TemplateView
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from syscore.views.tools import sysTools
import datetime
from syscore.views.tools import sysTools
from syscore.views.web import WebMachine

class SysInfoView(View):
    def __init__(self):
        self.webpageattributes = {
              "application_code": "sysinfo"
            , "application_name": "System Informations"
            , "module_code":      "sysinfo"
            , "module_template":  "sysinfo.html"
            , "module_name":      "System Informations"}
        self.webdata = {"htmlbody":""}
    def timeline(self):
        csdays = ["pondělí", "úterý", "středa", "čtvrtek", "pátek", "sobota", "neděle"]
        currdate = datetime.datetime.now()
        tl = f"today is <strong>{str(currdate.strftime("%A")).lower()}/{csdays[currdate.weekday()]} {str(currdate.date())}</strong>"
        tl = f"{tl}\n<br>\ncurrent time: <strong>{datetime.datetime.now().time().strftime("%H:%M")}</strong>"
        return tl
    def sessions(request):
        html_body = ""
        if request.session.get('loggeduser') is not None:
            loggeduser = request.session.get('loggeduser')
        else:
            loggeduser = "?"
        print(loggeduser)
    def get(self, request):
        self.webdata=["timeline",self.timeline()]
        return WebMachine.web_renderer(self, request, self.webpageattributes, self.webdata)

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
        """
        print ("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
        print (sysTools.showTuple(self,users,0))
        print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
        """
        return WebMachine.web_renderer(self, request, self.webpageattributes, self.webdata)