# 2026-11-11, robert.jiranek@gmail.com
# syslog.py - Logging module
#
from email.mime import text

from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from datetime import timedelta
from syslog.models import WebLog, SysLog
from syscor.views import WebMachine

class SysLogView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = ("syslog.view_syslog", "syslog.view_weblog")

    def has_permission(self):
        return any(
            self.request.user.has_perm(permission)
            for permission in self.get_permission_required()
        )

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()

        response = WebMachine.web_renderer(self, self.request, "403")
        response.status_code = 403
        return response

    def __init__(self):
        self.web_data = {}

    def get(self, request):
        self.web_data['weblog_count'] = WebLog.objects.count()
        self.web_data['syslog_count'] = SysLog.objects.count()

        """ -- test SysLog
        SysLogging.log(request, 'info', None,'syslog', 'SysLog Count', '', 'success'
                            , None, self.web_data['syslog_count'])
        SysLogging.log(request, 'info', None, 'syslog', 'WebLog Count','','success'
                            ,None, self.web_data['weblog_count'])
        """

        return WebMachine.web_renderer(self, request, 'syslog', self.web_data)

class SysLogging():
    def log(request, alert_code:str = "info", webmessage_show:str = "", module_code:str = "", action_code:str = ""
                    , step_code:str = "", status_code:str = "", parameters_value:dict = None, retval_value: str = ""
                    , error_code: str = "",error_message: str = ""
                    , webmessage_body: str = ""):

        alert_code = alert_code.lower()
        if webmessage_show:
            webmessage_show = webmessage_show.lower()

        web_msg = {}
        if webmessage_show in ('web', 'auth'):
            if not webmessage_body:
                if error_message:
                    webmessage_body = error_message
                else:
                    webmessage_body = retval_value
            web_msg = {'webmessage_show': webmessage_show, 'webmessage_body': webmessage_body}
            WebMachine.web_message_set(request, webmessage_body, message_alert=alert_code, message_type=webmessage_show)

        SysLog.objects.create(
            alert_code = alert_code.lower(),
            module_code = module_code.lower(),
            action_code = action_code,
            step_code = step_code,
            status_code = status_code.upper(),
            parameters_value = parameters_value,
            retval_value=retval_value,
            error_code=error_code,
            error_message=error_message,
            web_message=web_msg
        )
        return

class WebLogging():
    def log(request, module_code:str, module_file_template:str, web_page_attributes:dict, timedelta_render_page:timedelta,timedelta_content_prepare:timedelta ):
        WebLog.objects.create(
            module_code=module_code,
            module_file_template=module_file_template,
            web_page_attributes=web_page_attributes,
            timedelta_render_page=timedelta_render_page,
            timedelta_content_prepare=timedelta_content_prepare,
        )
        return

class SysLogListView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = "syslog.view_syslog"
    def __init__(self):
        self.web_data = {}

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()

        response = WebMachine.web_renderer(self, self.request, "403")
        response.status_code = 403
        return response

    def get(self, request):
        log_records = SysLog.objects.order_by('-timestamp')[:1000]
        self.web_data = {'syslogs': log_records}
        return WebMachine.web_renderer(self, request, 'sysloglist', self.web_data)

class WebLogListView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = "syslog.view_weblog"
    def __init__(self):
        self.web_data = {}

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()

        response = WebMachine.web_renderer(self, self.request, "403")
        response.status_code = 403
        return response

    def get(self, request):
        log_records = WebLog.objects.order_by('-timestamp')[:1000]
        self.web_data = {'weblogs': log_records}
        return WebMachine.web_renderer(self, request, 'webloglist', self.web_data)
