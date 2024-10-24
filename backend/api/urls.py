# This file defines the paths for the API
from django.urls import path
from .views import get_example, create_account, login, home
# from .views import function_name

urlpatterns = [
    path('example/', get_example, name='get_example'),
    path('signup/', create_account, name='signup'),
    path('login/', login, name='login')
]