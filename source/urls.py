from django.urls import path
from .views import *

app_name = "source"

urlpatterns = [
    path("connections/", ConnectionViewset.as_view({"get": "list"})),
]
