from django.urls import path
from .views import *

app_name = 'useragent'

urlpatterns = [
	path('browsers/', Browsers.as_view({'get': 'list'})),
]

