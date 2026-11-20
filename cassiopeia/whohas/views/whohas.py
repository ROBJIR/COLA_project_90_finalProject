from django.http.response import HttpResponse
from django.shortcuts import render
from django import forms
from django.contrib.auth.models import Group, Permission, User
from django.db import transaction
from django.db.models import Count, Prefetch
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views import View

from sysadm.forms import GroupDetailForm, PermissionDetailForm, UserDetailForm
from sysadm.views.base import SysInfoBase
from syscor.views.syscor import SysAuthNoPermission
from syscor.views.tools import sysTools
from syscor.views.web import WebRenderMixin

# Shows the Whohas landing page.
# Zobrazuje úvodní stránku Whohas.
class WhohasView(SysAuthNoPermission, WebRenderMixin, View):
    permission_required = "whohas.view_whohashomepage"
    # Initializes the page context.
    # Inicializuje kontext stránky.
    def __init__(self):
        self.webdata = {}
    # Renders the Whohas home page.
    # Vykresluje úvodní stránku Whohas.
    def get(self, request):
        return self.page_render(request, 'whohas', self.webdata)