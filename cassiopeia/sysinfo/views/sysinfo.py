from django.http.response import HttpResponse
from django.shortcuts import render, redirect
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
        self.webdata = {"webmain":""}
    def timeline(self):
        csdays = ["pondělí", "úterý", "středa", "čtvrtek", "pátek", "sobota", "neděle"]
        currdate = datetime.datetime.now()
        tl = f"today is <strong>{str(currdate.strftime("%A")).lower()}/{csdays[currdate.weekday()]} {str(currdate.date())}</strong>"
        tl = f"{tl}\n<br>\ncurrent time: <strong>{datetime.datetime.now().time().strftime("%H:%M")}</strong>"
        return tl
    def get(self, request):
        webmain = self.timeline()
        # print(self.webdata)
        self.webdata["webmain"] = webmain
        # print(self.webdata)
        return WebMachine.web_renderer(self, request, self.webpageattributes, self.webdata)

class SessionsInfoView(View):
    def __init__(self):
        self.webpageattributes = {
              "application_code": "sysinfo"
            , "application_name": "System Informations"
            , "module_code":      "sessionsinfo"
            , "module_template":  "sysinfo.html"
            , "module_name":      "Sessions Info"}
        self.webdata = {}
    def get(self,request):
        webmain = ""

        for session_key, session_value in request.session.items():
            webmain = f"{webmain}\n<tr><td>{session_key}</td><td>{session_value}</td><td>EDIT | DELETE</td></tr>"
            webmain = f"<table><tr><th>key</th><th>value</th><th>add sessions</th></tr>{html_body}</table>"

        if request.method == "GET":
            webmain = f"""{webmain}
                                <div>Add session...</div>
                                <div>
                                <form action="#" method="POST">
                                    <label>
                                        Key:
                                        <input type="text" name="key">
                                    </label>
                                    <label>
                                        Value:
                                        <input type="text" name="value">
                                    </label>
                                    <input type="submit">
                                </form>
                                </div>                            
                            """
        elif request.method == "POST":
            key = request.POST["key"]
            value = request.POST["value"]
            if key != "" and value != "":
                request.session[key] = value

                return redirect(self.webpageattributes)

        else:
            webmain = f"{webmain}<div>neco je spatne!</div>"

        self.webdata = ["webmain", webmain]
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