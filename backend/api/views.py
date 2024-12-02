import os
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from .models import Example, Account, EmailOTPDevice
from .serializer import ExampleSerializer, UserSerializer, AccountSerializer
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.models import User
from django.contrib import messages
from django.db import IntegrityError
from rest_framework.authtoken.models import Token
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from django.http import HttpResponse
from .serializer import EmailSerializer
from django.core.mail import send_mail
from django.http import HttpResponse
from .serializer import EmailSerializer
from dotenv import load_dotenv
from django.utils.timezone import now
from datetime import timedelta
from django_otp.util import random_hex

from .permissions import IsOwnerPermission

load_dotenv()

# Create your views here. This should contain all the actual functions run during an API call

@api_view(['GET'])
def get_example(request):
    return Response(ExampleSerializer({'name':'John'}).data)

@api_view(['POST'])
def signup(request):
    email = request.data.get("email")
    if request.data.get("email") and request.data.get("password"):
        try:
            serializer = UserSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                user = User.objects.get(username=request.data['email'])
                user.set_password(request.data['password'])
                user.save()
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
        account = Account.objects.get(owner=request.user,site=request.query_params.get("site"))
        serializer = AccountSerializer(instance=account)
        return Response({"account":serializer.data})
    except Account.DoesNotExist:
        return Response({}, status=status.HTTP_404_NOT_FOUND)
    
# @api_view(['POST'])
# def send_email(request):
#     if request.method == 'POST':
#         serializer = EmailSerializer(data=request.data)
#         if serializer.is_valid():
#             subject = serializer.validated_data['subject']
#             message = serializer.validated_data['message']
#             recipient = serializer.validated_data['recipient']
#             email_from = os.getenv('EMAIL_HOST_USER')

#             try:
#                 send_mail(subject, message, email_from, [recipient])
#                 return Response({"message": "Email sent successfully!"}, status=status.HTTP_200_OK)
#             except Exception as e:
#                 return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
#         else:
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def send_email(request):
    if request.method == 'POST':
        email = request.data.get('email')  # User's email address
        if not email:
            return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Generate OTP and save it
        try:
            otp_device = EmailOTPDevice()
            otp_device.generate_challenge(email=email)  # Pass email to the method
            return Response({"message": "OTP sent successfully!"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": f"Failed to save OTP: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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