# Configure the syslog Django application.
# Konfiguruje Django aplikaci syslog.
from django.apps import AppConfig


# Register the syslog application with Django.
# Registruje aplikaci syslog v Djangu.
class SyslogConfig(AppConfig):
    name = 'syslog'
