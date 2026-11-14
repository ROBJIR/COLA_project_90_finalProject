from django.http.response import HttpResponse
from django.shortcuts import render
from django.views import View
from syscor.views.web import WebMachine

class WhohasView(View):
    def __init__(self):
        self.webdata = {}
    def get(self, request):
        return WebMachine.web_renderer(self, request, 'whohas', self.webdata)