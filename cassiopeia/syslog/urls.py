from django.urls import path, include
from .views import *

urlpatterns = [
    path ('', SysLogView.as_view(), name = 'syslog'),
]
