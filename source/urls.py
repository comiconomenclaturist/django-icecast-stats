from django.urls import path
from .views import *

app_name = "source"

urlpatterns = [
    path("disconnection/", DisconnectionViewset.as_view({"get": "list"})),
]
