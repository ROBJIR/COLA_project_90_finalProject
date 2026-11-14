from django.urls import path, include
from .views import MainView, UserLogin, UserLogout, UserProfile, UserPasswordChange, UserProfile

urlpatterns = [
    path ('',           MainView.as_view(),         name = 'home'),
    path('cassiopeia',  MainView.as_view(),         name='cassiopeia'),
    path('sysadm',      include('sysadm.urls')),
    path('syslog',      include('syslog.urls')),
    path('whohas',      include('whohas.urls')),
    path('paidyet',     include('paidyet.urls')),
    path('profile',     UserProfile.as_view(),      name='profile'),
    path('changepassword', UserPasswordChange.as_view(), name='changepassword'),
    path('login',       UserLogin.as_view(),        name='login'),
    path('logout',      UserLogout.as_view(),       name='logout'),
]
