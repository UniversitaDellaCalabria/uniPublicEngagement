from django.urls import path
from pe_management.views import generic

app_name = 'template'

urlpatterns = [
    path('', generic.dashboard, name='dashboard'),
]
