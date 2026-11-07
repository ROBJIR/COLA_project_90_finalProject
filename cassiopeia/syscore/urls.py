from django.urls import path, include
from .views import UserLogin, UserLogout, UserProfile, UserPasswordChange, CoreView, UserProfile

urlpatterns = [
    path ('', CoreView.as_view(), name = 'home'),
    path('cassiopeia', CoreView.as_view(), name='cassiopeia'),
    path('sysinfo/', include('sysinfo.urls')),
    path('syslogging', include('syslogging.urls')),
    path('whohas',     include('whohas.urls')),
    path('paidyet',     include('paidyet.urls')),
    path('userprofile', UserProfile.as_view(), name='userprofile'),
    path('changepassword', UserPasswordChange.as_view(), name='changepassword'),
    path('login', UserLogin.as_view(), name='userlogin'),
    path('logout', UserLogout.as_view(), name='userlogout'),
]
