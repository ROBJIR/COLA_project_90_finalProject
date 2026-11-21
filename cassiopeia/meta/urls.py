from django.urls import path
from .views.meta import MetaView, DatabasesView

urlpatterns = [
    path("", MetaView.as_view(), name="meta"),
path("databases", DatabasesView.as_view(), name="databases"),
]
