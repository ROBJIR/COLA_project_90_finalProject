from django.http.response import HttpResponse
from django.shortcuts import render
from django.views import View
from syscore.views.web import WebMachine

class WhohasView(View):
    def __init__(self):
        self.webdata = {"empty","empty"}
        self.webpageattributes = {
                                  "application_code": "whohas"
                                , "application_name": "Who Has My Stuff?"
                                , "module_code": "whohas"
                                , "module_template": "whohas.html"
                                , "module_name": "Who Has My Stuff?"
                                }
    def get(self, request):
        return WebMachine.web_renderer(self, request, self.webpageattributes, self.webdata)