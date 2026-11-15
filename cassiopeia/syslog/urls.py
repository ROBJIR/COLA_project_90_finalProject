# Route log overview, list, and permission-protected clearing requests.
# Směruje požadavky na přehled, seznamy a mazání logů chráněné oprávněními.
from django.urls import path
from .views.syslog import (
    PythonLogClearView,
    PythonLogListView,
    SysLogClearView,
    SysLogListView,
    SysLogView,
    WebLogClearView,
    WebLogListView,
)

urlpatterns = [
    path ('', SysLogView.as_view(), name = 'syslog'),
    path('webloglist', WebLogListView.as_view(), name='webloglist'),
    path('sysloglist', SysLogListView.as_view(), name='sysloglist'),
    path("syslogclear", SysLogClearView.as_view(), name="syslogclear"),
    path("weblogclear", WebLogClearView.as_view(), name="weblogclear"),
    path("pythonloglist", PythonLogListView.as_view(), name="pythonloglist"),
    path("pythonlogclear", PythonLogClearView.as_view(), name="pythonlogclear"),
]
