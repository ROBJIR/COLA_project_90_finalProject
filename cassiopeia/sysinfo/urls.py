from django.urls import path, include
from .views import SysInfoView, SysInfoUserList

urlpatterns = [
    path ('', SysInfoView.as_view(), name = 'sysinfo'),
    path ('userlist', SysInfoUserList.as_view(), name = 'sysinfo-userlist'),
]
