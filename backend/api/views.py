from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Example
from .serializer import ExampleSerializer
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.models import User
from django.contrib import messages
from django.db import IntegrityError

# Create your views here. This should contain all the actual functions run during an API call

@api_view(['GET'])
def get_example(request):
    return Response(ExampleSerializer({'name':'John'}).data)

# Creates user account/Sign up page
def create_account(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        if username and password:
            try:
                user = User.objects.create_user(username=username, password=password)
                user.save()
                messages.success(request, 'Account created successfully!')
                return redirect('login')
            except IntegrityError:
                messages.error(request, "Username already exists.")
        else:
            messages.error(request, "Please fil in all fields.")
    return render(request, 'signup.html')

#Login screen for users to log in
def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        if username and password:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                auth_login(request, user)
                messages.success(request, 'Login successful!')
                return redirect('home')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Please enter both a username and a password.')

    return render(request, 'login.html')

#Home page
def home(request):
    if request.user.is_authenticated:
        return render(request, 'home.html', {'username': request.user.username})
    else:
        return redirect('login')