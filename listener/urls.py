from django.urls import path
from .views import *

app_name = 'listener'

# app_name will help us do a reverse look-up later.
urlpatterns = [
    path('aggregate/', AggregateView.as_view()),
    path('count/', CountViewSet.as_view({'get': 'list'})),
    path('count2/', Count2ViewSet.as_view()),
    path('hours/', HoursViewSet.as_view({'get': 'list'})),
    path('countries/', CountriesViewSet.as_view({'get': 'list'})),
    path('referer/', RefererViewSet.as_view({'get': 'list'})),
]