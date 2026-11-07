from django.urls import path, include
from .views import SysInfoView, SysInfoUserList, SessionsInfoView

urlpatterns = [
    path ('', SysInfoView.as_view(), name = 'sysinfo'),
    path ('userlist', SysInfoUserList.as_view(), name = 'sysinfo-userlist'),
    path ('Sessionsinfo', SessionsInfoView.as_view(), name = 'sysinfo-Sessionsinfo'),
]
