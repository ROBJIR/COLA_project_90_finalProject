from django.urls import path, include
from .views import *

urlpatterns = [
    path ('', SysLogView.as_view(), name = 'syslog'),
    path('webloglist', WebLogListView.as_view(), name='webloglist'),
    path('sysloglist', SysLogListView.as_view(), name='sysloglist'),
]
