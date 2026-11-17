# Display permission-protected log summaries and lists and handle log-clearing POST requests.
# Zobrazuje přehledy a seznamy logů chráněné oprávněními a zpracovává požadavky POST na jejich vymazání.
# 2026-11-11, robert.jiranek@gmail.com
# syslog.py - Logging module
#
from django.shortcuts import redirect
from django.views import View
from syscor.views import SysAuthNoPermission
from syslog.models import WebLog, SysLog
from syscor.views import WebMachine
from syscor.models import PythonLog

# Display permitted log summaries.
# Zobrazuje přehledy logů podle oprávnění.
class SysLogView(SysAuthNoPermission, View):
    permission_required = ("syslog.view_syslog", "syslog.view_weblog","syscor.view_pythonlog",)

    def has_permission(self):
        return any(
            self.request.user.has_perm(permission)
            for permission in self.get_permission_required()
        )

    def get(self, request):
        self.web_data = {}
        if request.user.has_perm("syslog.view_syslog"):
            self.web_data["syslog_count"] = SysLog.objects.count()

        if request.user.has_perm("syslog.view_weblog"):
            self.web_data["weblog_count"] = WebLog.objects.count()

        if request.user.has_perm("syscor.view_pythonlog"):
            self.web_data["pythonlog_count"] = PythonLog.objects.count()

        return WebMachine.web_renderer(self, request, 'syslog', self.web_data)

# List recent application events.
# Vypisuje poslední aplikační události.
class SysLogListView(SysAuthNoPermission, View):
    permission_required = "syslog.view_syslog"
    def get(self, request):
        log_records = SysLog.objects.order_by("-timestamp", "-id")[:100]
        self.web_data = {'syslogs': log_records}
        return WebMachine.web_renderer(self, request, 'sysloglist', self.web_data)

# List recent web rendering records.
# Vypisuje poslední záznamy vykreslování stránek.
class WebLogListView(SysAuthNoPermission, View):
    permission_required = "syslog.view_weblog"
    def get(self, request):
        log_records = WebLog.objects.order_by("-timestamp", "-id")[:100]
        self.web_data = {'weblogs': log_records}
        return WebMachine.web_renderer(self, request, 'webloglist', self.web_data)

# List recent Python log records.
# Vypisuje poslední záznamy Python logu.
class PythonLogListView(SysAuthNoPermission, View):
    permission_required = "syscor.view_pythonlog"

    def get(self, request):
        logs = PythonLog.objects.order_by("-timestamp", "-id")[:100]
        return WebMachine.web_renderer(
            self, request, "pythonloglist", {"pythonlogs": logs}
        )


# Clear Python logs after checking delete permission.
# Maže Python logy po kontrole oprávnění k mazání.
class PythonLogClearView(SysAuthNoPermission, View):
    permission_required = "syscor.delete_pythonlog"

    def post(self, request):
        PythonLog.objects.all().delete()
        return redirect("pythonloglist")

# Clear application logs after checking delete permission.
# Maže aplikační logy po kontrole oprávnění k mazání.
class SysLogClearView(SysAuthNoPermission, View):
    permission_required = "syslog.delete_syslog"

    def post(self, request):
        SysLog.objects.all().delete()
        return redirect("sysloglist")

# Clear web logs after checking delete permission.
# Maže webové logy po kontrole oprávnění k mazání.
class WebLogClearView(SysAuthNoPermission, View):
    permission_required = "syslog.delete_weblog"

    def post(self, request):
        WebLog.objects.all().delete()
        return redirect("webloglist")

