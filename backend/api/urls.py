# This file defines the paths for the API
from django.urls import path
from .views import get_example, create_account, login, home, signup, get_auth, test_token, add_account, get_account
# from .views import function_name

urlpatterns = [
    path('example/', get_example, name='get_example'),
    path('signup', signup, name='signup'),
    path('login', get_auth, name='get_auth'),
    path('test_token/', test_token, name='test_token'),
    path('add_account', add_account, name='add_account'),
    path('account', get_account, name='get_account')
]