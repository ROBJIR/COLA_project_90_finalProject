from django.http.response import HttpResponse
from django.shortcuts import render
from django.views import View
from .web import WebMachine
import datetime

class CoreView(View):
    def __init__(self):
        self.webpageattributes = {
                  "application_code": "cassiopeia"
                , "application_name": "Cassiopeia Projects"
                , "module_code": "cassiopeia"
                , "module_template": "core-main.html"
                , "module_name": "Cassiopeia Project"}
        self.webdata = {"empty","empty"}
    def get(self, request):
        return WebMachine.web_renderer(self, request, self.webpageattributes, self.webdata)


