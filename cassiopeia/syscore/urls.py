from django.urls import path, include
from .views import sysLogin, sysLogout, CoreView

urlpatterns = [
    path ('', CoreView.as_view(), name = 'home'),
    path('cassiopeia', CoreView.as_view(), name='cassiopeia'),
    path('sysinfo/', include('sysinfo.urls')),
    path('syslogging', include('syslogging.urls')),
    path('whohas',     include('whohas.urls')),
    path('paidyet',     include('paidyet.urls')),
    path('syslogin', sysLogin.as_view(), name='syslogin'),
    path('syslogout', sysLogout.as_view(), name='syslogout'),
]
