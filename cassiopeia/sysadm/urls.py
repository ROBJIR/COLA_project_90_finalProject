# Route summaries, authentication details, and request diagnostics.
# Směruje přehledy, detaily autentizace a diagnostiku požadavků.
from django.urls import path
from .views import (
    SysAdmView,
    SessionsInfoView,
    CookiesInfoView,
    SysInfoUserList,
    SysInfoUserDet,
    SysInfoGroupList,
    SysInfoGroupDet,
    SysInfoPermissionList,
    SysInfoPermissionDet,
)

urlpatterns = [
    path('', SysAdmView.as_view(), name='sysadm'),
    path('userlist', SysInfoUserList.as_view(), name='sysadm-userlist'),
    path('userdet/', SysInfoUserList.as_view(), name='sysadm-userdet-no'),
    path('userdet/<int:userid>', SysInfoUserDet.as_view(), name='sysadm-userdet'),
    path('grouplist', SysInfoGroupList.as_view(), name='sysadm-grouplist'),
    path('groupdet/<int:groupid>', SysInfoGroupDet.as_view(), name='sysadm-groupdet'),
    path('permissiondet/<int:permissionid>', SysInfoPermissionDet.as_view(), name='sysadm-permissiondet'),
    path('permissionlist', SysInfoPermissionList.as_view(), name='sysadm-permissionlist'),

    path('sessionsinfo', SessionsInfoView.as_view(), name='sysadm-sessionsinfo'),
    path('cookiesinfo', CookiesInfoView.as_view(), name='sysadm-cookiesinfo'),
]
