from django.urls import path, include
from .views import SessionsInfoView, SysInfoView, SysInfoUserList

urlpatterns = [
    path ('', SysInfoView.as_view(), name = 'sysinfo'),
    path ('userlist', SysInfoUserList.as_view(), name = 'sysinfo-userlist'),
    path ('Sessionsinfo', SessionsInfoView.as_view(), name = 'sysinfo-sessionsinfo'),
]
