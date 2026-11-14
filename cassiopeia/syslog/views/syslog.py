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

class SysLogView(View):
    def __init__(self):
        self.web_data = {}
    def get(self, request):
        return WebMachine.web_renderer(self, request, 'syslog', self.web_data)