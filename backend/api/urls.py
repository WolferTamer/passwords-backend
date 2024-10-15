# This file defines the paths for the API
from django.urls import path
from .views import get_example
# from .views import function_name

urlpatterns = [
    path('example/', get_example, name='get_example'),
]