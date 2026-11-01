from django.urls import path, include
from .views import *

urlpatterns = [
    path ('', WhohasView.as_view(), name = 'whohas'),
]
