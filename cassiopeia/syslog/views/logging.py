# Persist application events and rendering measurements with file and console fallback on database errors.
# Ukládá aplikační události a měření vykreslování a při chybách databáze používá náhradní zápis do souboru a konzole.
# 2026-11-11, robert.jiranek@gmail.com
# logging.py - Logging module
#
import logging
from django.db import DatabaseError, transaction
from datetime import timedelta
from syslog.models import WebLog, SysLog
from syscor.views import WebMachine

logger = logging.getLogger("cassiopeia.database_fallback")

# Write application events with database error fallback.
# Zapisuje aplikační události s náhradním logováním při chybě databáze.
class SysLogging:
    # Records an application event and any accompanying user message.
    # Zaznamenává aplikační událost a případnou zprávu pro uživatele.
    @staticmethod
    def log(
        request,
        alert_code: str = "info",
        webmessage_show: str | None = "",
        module_code: str = "",
        action_code: str = "",
        step_code: str | None = "",
        status_code: str = "",
        parameters_value: dict | None = None,
        retval_value: str = "",
        error_code: str | None = "",
        error_message: str | None = "",
        webmessage_body: str = "",
    ) -> bool:
        """Store an application event; return False on a database error."""

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
        try:
            with transaction.atomic():
                SysLog.objects.create(
                    alert_code = alert_code,
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

        except DatabaseError:
            logger.exception("SysLogging.log(): The record could not be saved to table SysLog.")
            return False

        return True

# Write rendering metrics with database error fallback.
# Zapisuje měření vykreslování s náhradním logováním při chybě databáze.
class WebLogging:
    # Records web page preparation and rendering times.
    # Zaznamenává dobu přípravy a vykreslování webové stránky.
    @staticmethod
    def log(
        request,
        module_code: str,
        module_file_template: str,
        web_page_attributes: dict,
        timedelta_render_page: timedelta,
        timedelta_content_prepare: timedelta,
    ) -> bool:
        """Store rendering metrics; return False on a database error."""
        try:
            with transaction.atomic():
                WebLog.objects.create(
                    module_code=module_code,
                    module_file_template=module_file_template,
                    web_page_attributes=web_page_attributes,
                    timedelta_render_page=timedelta_render_page,
                    timedelta_content_prepare=timedelta_content_prepare,
                )
        except DatabaseError:
            logger.exception("WebLogging.log(): The record could not be saved to table WebLog.")
            return False

        return True


