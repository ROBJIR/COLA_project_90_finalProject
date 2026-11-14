from django.http.response import HttpResponse
from django.shortcuts import render
from django.views import View
from syscor.views.web import WebMachine

class PaidyetView(View):
    def __init__(self):
        self.webdata = {}
    def get(self, request):
        return WebMachine.web_renderer(self, request, 'paidyet', self.webdata)