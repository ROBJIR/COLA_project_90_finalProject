from django.http.response import HttpResponse
from django.shortcuts import render
from django.views import View

from django.views import View

from sysadm.forms import GroupDetailForm, PermissionDetailForm, UserDetailForm
from sysadm.views.base import SysInfoBase
from syscor.views.syscor import SysAuthNoPermission
from syscor.views.tools import sysTools

# Shows the Paidyet landing page to authorized users.
# Zobrazuje úvodní stránku Paidyet oprávněným uživatelům.
class PaidyetView(SysAuthNoPermission, View):
    permission_required = "paidyet.view_paidyethomepage"
    # Initializes the page context.
    # Inicializuje kontext stránky.
    def __init__(self):
        self.web_data = {}
    # Renders the Paidyet home page.
    # Vykresluje úvodní stránku Paidyet.
    def get(self, request):
        return self.page_render(request, 'paidyet', self.web_data)