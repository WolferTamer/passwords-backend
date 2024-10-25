from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from .models import Example, Account
from .serializer import ExampleSerializer, UserSerializer, AccountSerializer
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.models import User
from django.contrib import messages
from django.db import IntegrityError
from rest_framework.authtoken.models import Token
from django.shortcuts import get_object_or_404

from .permissions import IsOwnerPermission


# Create your views here. This should contain all the actual functions run during an API call

@api_view(['GET'])
def get_example(request):
    return Response(ExampleSerializer({'name':'John'}).data)

@api_view(['POST'])
def signup(request):
    if request.data["username"] and request.data["password"]:
        try:
            serializer = UserSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                user = User.objects.get(username=request.data['username'])
                user.set_password(request.data['password'])
                user.save
                token = Token.objects.create(user=user)
                return Response({"token":token.key,"user":serializer.data}, status=status.HTTP_201_CREATED)
        except IntegrityError:
            return Response({"error":"Username Already in Use"},status=status.HTTP_400_BAD_REQUEST)
    return Response({"error":"Username or Password not provided"},status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['POST'])
def get_auth(request):
    user = get_object_or_404(User, username=request.data['username'])
    if not user.check_password(request.data['password']):
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
    token, created = Token.objects.get_or_create(user=user)
    serializer = UserSerializer(instance=user)
    return Response({"token":token.key,"user":serializer.data}, status=status.HTTP_200_OK)

@api_view(['GET'])
@authentication_classes([SessionAuthentication,TokenAuthentication])
@permission_classes([IsAuthenticated])
def test_token(request):
    return Response("Passed for {}".format(request.user.username))

@api_view(['POST'])
@authentication_classes([SessionAuthentication,TokenAuthentication])
@permission_classes([IsAuthenticated])
def add_account(request):
    data = request.data
    if data["username"] and data["password"] and data["site"] and data["title"]:
        try:
            account = Account.objects.create(username=data["username"],password=data["password"],site=data["site"],title=data["title"],owner=request.user)
            serializer = AccountSerializer(account)
            return Response({"account":serializer.data}, status=status.HTTP_201_CREATED)
        except IntegrityError:
            return Response({"errors":"Had an integrity error"},status=status.HTTP_400_BAD_REQUEST)
    return Response({},status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@authentication_classes([SessionAuthentication,TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_account(request):
    try:
        account = Account.objects.get(owner=request.user,site=request.data["site"])
        serializer = AccountSerializer(instance=account)
        return Response({"account":serializer.data})
    except Account.DoesNotExist:
        return Response({}, status=status.HTTP_404_NOT_FOUND)

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