# Register the system administration application with Django.
# Registruje aplikaci systémové administrace v Django.
from django.apps import AppConfig


# Identify the administration application for Django.
# Určuje aplikaci administrace pro Django.
class SysinfoConfig(AppConfig):
    name = 'sysadm'
