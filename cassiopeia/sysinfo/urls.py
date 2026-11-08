from django.urls import path, include
from .views import SessionsInfoView, CookiesInfoView, SysInfoView, SysInfoUserList

urlpatterns = [
    path('', SysInfoView.as_view(), name = 'sysinfo'),
    path('userlist', SysInfoUserList.as_view(), name = 'sysinfo-userlist'),
    path('sessionsinfo', SessionsInfoView.as_view(), name = 'sysinfo-sessionsinfo'),
    path('cookiesinfo', CookiesInfoView.as_view(), name='sysinfo-cookiesinfo'),
]
