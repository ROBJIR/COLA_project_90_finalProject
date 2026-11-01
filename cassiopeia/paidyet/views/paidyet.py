from django.http.response import HttpResponse
from django.shortcuts import render
from django.views import View
from syscore.views.web import WebMachine

class PaidyetView(View):
    def __init__(self):
        self.webdata = {"empty","empty"}
        self.webpageattributes = {
                                  "application_code": "paidyet"
                                , "application_name": "Paid yet?"
                                , "module_code": "paidyet"
                                , "module_template": "paidyet.html"
                                , "module_name": "Paid yet?"
                                }
    def get(self, request):
        return WebMachine.web_renderer(self, request, self.webpageattributes, self.webdata)