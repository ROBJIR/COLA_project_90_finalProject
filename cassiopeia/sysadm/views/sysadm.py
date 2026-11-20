# Display administration summaries and permission-protected authentication records.
# Zobrazuje přehled administrace a záznamy autentizace chráněné oprávněními.
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
from syscor.views.web import WebMachine


# Display the system administration dashboard.
# Zobrazuje přehled systémové administrace.
class SysAdmView(SysAuthNoPermission, View):
    permission_required = "sysadm.view_dashboard"

    # Prepare page data and render the requested administration view.
    # Připravuje data stránky a vykresluje požadovaný pohled administrace.
    def get(self, request):
        data = {
            "sysinfo": SysInfoBase.SysInfoSystem(),
            "dbsinfo": SysInfoBase.SysInfoDatabase(),
            "usersinfo": SysInfoBase.SysInfoUsers(),
            "errors24h": SysInfoBase.SysInfoErrors(),
            "webinfo": SysInfoBase.SysInfoWeb(),
        }
        return self.page_render(request, 'sysadm', data)

# Inspect the current request session after permission checks.
# Po kontrole oprávnění zobrazuje session aktuálního požadavku.
class SessionsInfoView(SysAuthNoPermission, View):
    permission_required = "sysadm.view_sessionlist"

    # Prepare page data and render the requested administration view.
    # Připravuje data stránky a vykresluje požadovaný pohled administrace.
    def get(self, request):
        sessions = dict(request.session.items())
        data = sysTools.dictionary_to_data(sessions)
        web_data = {
            "html_table": WebMachine.dictionary_to_html_table(data),
        }
        return self.page_render(
            request,
            'sessionsinfo',
            web_data,
        )

# Inspect cookies received with the current request.
# Zobrazuje cookies přijaté v aktuálním požadavku.
class CookiesInfoView(SysAuthNoPermission, View):
    permission_required = "sysadm.view_cookielist"

    # Prepare page data and render the requested administration view.
    # Připravuje data stránky a vykresluje požadovaný pohled administrace.
    def get(self, request):
        cookies = dict(request.COOKIES.items())
        data = sysTools.dictionary_to_data(cookies)
        web_data = {
            "html_table": WebMachine.dictionary_to_html_table(data),
        }
        return self.page_render(
            request,
            'cookieinfo',
            web_data,
        )

# List user accounts ordered by username.
# Vypisuje uživatelské účty seřazené podle jména.
class SysInfoUserList(SysAuthNoPermission, View):
    permission_required = "auth.view_user"

    # Prepare page data and render the requested administration view.
    # Připravuje data stránky a vykresluje požadovaný pohled administrace.
    def get(self, request):
        users = list(User.objects.order_by("username"))
        table_row_count = len(users)
        web_data = {"users": users, "table_row_count": table_row_count}
        return self.page_render(request, 'sysadm-userlist', web_data)


# Share read-only display, authorized editing, and atomic saving.
# Sdílí zobrazení, autorizovanou editaci a atomické ukládání.
class AuthDetailView(SysAuthNoPermission, View):
    # Require view access and change access for editing or POST.
    # Vyžaduje právo prohlížení a při editaci či POST také právo změny.
    def get_permission_required(self):
        permissions = [f'auth.view_{self.model._meta.model_name}']
        if self.request.method == 'POST' or self.request.GET.get('edit') == '1':
            permissions.append(f'auth.change_{self.model._meta.model_name}')
        return tuple(permissions)

    # Check whether the current actor may edit this record.
    # Ověřuje, zda aktuální uživatel smí tento záznam upravit.
    def can_edit(self, request, obj):
        return request.user.has_perm(f'auth.change_{self.model._meta.model_name}')

    # Bind model data and pass the acting user to account forms.
    # Navazuje modelová data a předává správce formuláři uživatele.
    def get_form(self, request, obj, data=None):
        kwargs = {'instance': obj, 'data': data}
        if self.model in (User, Group):
            kwargs['actor'] = request.user
        return self.form_class(**kwargs)

    # Supply permitted related records for the detail template.
    # Dodává povolené související záznamy pro šablonu detailu.
    def get_related_data(self, request, obj):
        return {}

    # Prepare widget styles and render a read-only or editable detail.
    # Připravuje vzhled polí a vykresluje detail pro čtení nebo editaci.
    def show(self, request, obj, form, editing=False, status=200):
        for field in form.fields.values():
            field.disabled = not editing
            field.widget.attrs['class'] = (
                'form-check-input' if isinstance(field.widget, forms.CheckboxInput)
                else 'form-select' if isinstance(field.widget, forms.Select)
                else 'form-control'
            )
        data = {
            'detail': obj, 'form': form, 'form_enabled': editing,
            'can_edit': self.can_edit(request, obj),
            'detail_url': self.detail_url, 'list_url': self.list_url,
            'saved': request.GET.get('saved') == '1',
        }
        data.update(self.get_related_data(request, obj))
        response = self.page_render(request, self.module_code, data)
        response.status_code = status
        return response

    # Prepare page data and render the requested administration view.
    # Připravuje data stránky a vykresluje požadovaný pohled administrace.
    def get(self, request, **kwargs):
        obj = get_object_or_404(self.model, pk=kwargs[self.pk_argument])
        editing = request.GET.get('edit') == '1'
        if editing and not self.can_edit(request, obj):
            return self.handle_no_permission()
        return self.show(request, obj, self.get_form(request, obj), editing)

    # Validate and atomically save changes, or display validation errors.
    # Ověřuje a atomicky ukládá změny, případně zobrazí chyby validace.
    def post(self, request, **kwargs):
        obj = get_object_or_404(self.model, pk=kwargs[self.pk_argument])
        if not self.can_edit(request, obj):
            return self.handle_no_permission()
        form = self.get_form(request, obj, request.POST)
        if form.is_valid():
            with transaction.atomic():
                form.save()
            return redirect(reverse(self.detail_url, args=[obj.pk]) + '?saved=1')
        return self.show(request, obj, form, editing=True, status=400)


# Edit account details while protecting privileged accounts.
# Upravuje údaje účtu a chrání privilegované účty.
class SysInfoUserDet(AuthDetailView):
    model = User
    form_class = UserDetailForm
    pk_argument = 'userid'
    module_code = detail_url = 'sysadm-userdet'
    list_url = 'sysadm-userlist'

    # Check whether the current actor may edit this record.
    # Ověřuje, zda aktuální uživatel smí tento záznam upravit.
    def can_edit(self, request, obj):
        return super().can_edit(request, obj) and (
            request.user.is_superuser or not (obj.is_superuser or obj.is_staff)
        )


# Display group permissions and authorized member links.
# Zobrazuje oprávnění skupiny a odkazy na členy podle oprávnění.
class SysInfoGroupDet(AuthDetailView):
    model = Group
    form_class = GroupDetailForm
    pk_argument = 'groupid'
    module_code = detail_url = 'sysadm-groupdet'
    list_url = 'sysadm-grouplist'

    # Supply permitted related records for the detail template.
    # Dodává povolené související záznamy pro šablonu detailu.
    def get_related_data(self, request, obj):
        if request.user.has_perm('auth.view_user'):
            return {'members': obj.user_set.order_by('username')}
        return {}


# Display and edit an authentication permission.
# Zobrazuje a upravuje oprávnění autentizace.
class SysInfoPermissionDet(AuthDetailView):
    model = Permission
    form_class = PermissionDetailForm
    pk_argument = 'permissionid'
    module_code = detail_url = 'sysadm-permissiondet'
    list_url = 'sysadm-permissionlist'

    # Reserve changes to permission definitions for superusers.
    # Vyhrazuje změny definic oprávnění superuživatelům.
    def can_edit(self, request, obj):
        return request.user.is_superuser and super().can_edit(request, obj)

# List groups with permissions and member counts.
# Vypisuje skupiny, jejich oprávnění a počty členů.
class SysInfoGroupList(SysAuthNoPermission, View):
    permission_required = "auth.view_group"

    # Prepare page data and render the requested administration view.
    # Připravuje data stránky a vykresluje požadovaný pohled administrace.
    def get(self, request):
        groups = Group.objects.prefetch_related(
            Prefetch('permissions', queryset=Permission.objects.select_related('content_type')),
        ).annotate(member_count=Count('user')).order_by("name")
        web_data = {"groups": groups}
        return self.page_render(request, 'sysadm-grouplist', web_data)

# List permissions together with their application and model.
# Vypisuje oprávnění společně s aplikací a modelem.
class SysInfoPermissionList(SysAuthNoPermission, View):
    permission_required = "auth.view_permission"

    # Prepare page data and render the requested administration view.
    # Připravuje data stránky a vykresluje požadovaný pohled administrace.
    def get(self, request):
        permissions = Permission.objects.select_related('content_type').order_by('content_type__app_label', 'codename')
        web_data = {"permissions": permissions}
        return self.page_render(request, 'sysadm-permissionlist', web_data)
