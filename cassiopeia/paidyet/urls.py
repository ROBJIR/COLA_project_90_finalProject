from django.urls import path, include
from .views import *

urlpatterns = [
    path ('', PaidyetView.as_view(), name = 'paidyet'),
]
