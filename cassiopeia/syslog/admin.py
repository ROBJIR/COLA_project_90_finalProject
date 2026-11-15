from django.contrib import admin
from .models import WebLog, SysLog


@admin.register(WebLog)
class WebLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'module_code', 'timedelta_content_prepare','timedelta_render_page')
    list_filter = ('module_code',)
    search_fields = ('module_code', 'module_file_template')
    ordering = ('-timestamp',)


@admin.register(SysLog)
class SysLogAdmin(admin.ModelAdmin):
    list_display = (
        'timestamp',
        'alert_code',
        'module_code',
        'action_code',
        'step_code',
        'status_code',
        'error_code',
    )
    list_filter = ('module_code', 'alert_code', 'action_code','status_code','error_code')
    search_fields = ('module_code', 'alert_code', 'error_code', 'error_message')
    ordering = ('-timestamp',)