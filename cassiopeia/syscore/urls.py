from django.urls import path, include
from .views import MainView, UserLogin, UserLogout, UserProfile, UserPasswordChange, UserProfile

urlpatterns = [
    path ('', MainView.as_view(), name = 'home'),
    path('cassiopeia', MainView.as_view(), name='cassiopeia'),
    path('sysadm', include('sysadm.urls')),
    path('syslogging', include('syslogging.urls')),
    path('whohas',     include('whohas.urls')),
    path('paidyet',     include('paidyet.urls')),
    path('userprofile', UserProfile.as_view(), name='userprofile'),
    path('changepassword', UserPasswordChange.as_view(), name='changepassword'),
    path('login', UserLogin.as_view(), name='userlogin'),
    path('logout', UserLogout.as_view(), name='userlogout'),
]
