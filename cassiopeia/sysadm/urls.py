from django.urls import path, include
from .views import SessionsInfoView, CookiesInfoView, SysInfoView, SysInfoUserList

urlpatterns = [
    path('', SysInfoView.as_view(), name = 'sysadm'),
    path('userlist', SysInfoUserList.as_view(), name = 'sysadm-userlist'),
    path('sessionsinfo', SessionsInfoView.as_view(), name = 'sysadm-sessionsinfo'),
    path('cookiesinfo', CookiesInfoView.as_view(), name='sysadm-cookiesinfo'),
]
