from django.db import models

# Create your models here.
class WebLog(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    module_code = models.CharField(max_length=32, null=True, db_index=True)
    timedelta_content_prepare = models.DurationField(null=True)
    timedelta_render_page = models.DurationField(null=True)
    web_page_attributes = models.JSONField(default=dict, null=True)
    module_file_template = models.CharField(max_length=120, null=True)

class SysLog(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    alert_code = models.CharField(max_length=12, null=True, db_index=True)
    module_code = models.CharField(max_length=32, null=True, db_index=True)
    action_code = models.CharField(max_length=32, null=True, db_index=True)
    step_code = models.CharField(max_length=32, null=True, db_index=True)
    status_code = models.CharField(max_length=12, null=True, db_index=True)
    parameters_value = models.JSONField(default=dict, null=True)
    retval_value = models.TextField(null=True)
    error_code = models.CharField(max_length=120, null=True, db_index=True)
    error_message = models.TextField(null=True)
    web_message = models.JSONField(default=dict, null=True)


