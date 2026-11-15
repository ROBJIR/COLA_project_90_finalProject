from django.urls import path, include
from .views import *

urlpatterns = [
    path('', SysAdmView.as_view(), name = 'sysadm'),
    path('userlist', SysInfoUserList.as_view(), name = 'sysadm-userlist'),
    path('grouplist', SysInfoGroupList.as_view(), name = 'sysadm-grouplist'),
    path('permissionlist', SysInfoPermissionList.as_view(), name = 'sysadm-permissionlist'),

    path('sessionsinfo', SessionsInfoView.as_view(), name = 'sysadm-sessionsinfo'),
    path('cookiesinfo', CookiesInfoView.as_view(), name='sysadm-cookiesinfo'),
]
