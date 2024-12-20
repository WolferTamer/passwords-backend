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
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .cryption import encryption, decrypt_msg, gen_key
from .key_storage import store_user_key, get_user_key
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

    if request.data.get("email") and request.data.get("password"):
        try:
            serializer = UserSerializer(data=request.data)
            if serializer.is_valid():
                user = User(username=request.data['email'], email=request.data['email'])                
                user.set_password(request.data['password'])
                user.save()
                #storing the user's encryption key in key storage file
                key = store_user_key(request.data['email'])
                token = Token.objects.create(user=user)
                return JsonResponse({"token":token.key,"user":serializer.data, "encryption_key": key.hex()}, status=status.HTTP_201_CREATED)
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
    if data["username"] and data["password"] and data["site"]:
        try:
            # encryption key for logged in user
            key = get_user_key(request.user.username)
            if not key:
                return Response({"error": "Encyption key is not found for the user."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            encrypted_password = encryption(data["password"], key)

            # changing password=data["password"] to password=encrypted_password
            account = Account.objects.create(username=data["username"],encrypted_password=encrypted_password,site=data["site"],title="test",owner=request.user)
            serializer = AccountSerializer(account)
            return Response({"account":serializer.data}, status=status.HTTP_201_CREATED)
        except IntegrityError as e:
            print("Integrety: ", e)
            return Response({"errors":"Had an integrity error"},status=status.HTTP_400_BAD_REQUEST)
    return Response({},status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@authentication_classes([SessionAuthentication,TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_account(request):
    site = request.query_params.get("site")
    if not site:
        return Response({"error": "Site parameter is required."}, status=status.HTTP_400_BAD_REQUEST)
    try:
        account = Account.objects.get(owner=request.user,site=site)
        key = get_user_key(request.user.username)
        if not key:
            return Response({"error": "Encryption key not found for the user."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        decrypted_password = decrypt_msg(account.encrypted_password, key)
        serializer = AccountSerializer(instance=account)
        #adding decrypted password to serialized account data
        account_data = serializer.data
        account_data["decrypted_password"] = decrypted_password

        site=request.query_params.get("site")
        otp_device, created = EmailOTPDevice.objects.get_or_create(user=request.user,email=request.user.email) # Check if OTP exists for the user
        token = request.query_params.get("token")
        print(token)
        print(site)
        if token:
            if otp_device.verify_token(token): # Uses verify_token from EmailOTPDevide to validate token
                # If the token is valid, return the account information
                return Response({"message": "OTP sent successfully", 
                                "account":account_data}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Invalid or expired OTP code."}, status=400)
        # If there is no code sent, send a new OTP
        try:
            otp_device.generate_challenge(email=request.user.email)
            return Response({"message": "OTP sent successfully"}, status=status.HTTP_200_OK)
        except Exception as e:
                    return Response({"error": f"Failed to sent OTP: {str(e)}"},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Account.DoesNotExist:
        return Response({}, status=status.HTTP_404_NOT_FOUND)

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