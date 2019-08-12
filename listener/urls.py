from django.urls import path
from .views import *

app_name = 'listener'

# app_name will help us do a reverse look-up later.
urlpatterns = [
    path('aggregate/', AggregateView.as_view()),
    path('new-aggregate/', NewListenerAggregateView.as_view({'get': 'list'})),
    path('countries/', CountriesViewSet.as_view({'get': 'list'})),
    path('referer/', RefererViewSet.as_view({'get': 'list'})),
]