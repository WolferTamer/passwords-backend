from django.db import models
from django.contrib.auth.models import User
from django_otp.models import Device
from django.core.mail import send_mail
from django_otp.util import random_hex
from django.utils.timezone import now
from datetime import timedelta
import random
import string

# Create your models here. This is where things such as User objects should be defined.
class Example(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
# Account is a saved password/account pair to be returned, not the one they made with us.
class Account(models.Model):
    title = models.CharField(max_length=100)
    site = models.CharField(max_length=100)
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='User', default=1)

    def __str__(self):
        return self.title
    
def random_hex(length):
    return ''.join(random.choices(string.digits, k=length))

class EmailOTPDevice(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Linking to the User model
    email = models.EmailField(unique=True)  # User's email address
    token = models.CharField(max_length=6, blank=True, null=True)  # OTP code
    created_at = models.DateTimeField(blank=True, null=True)  # Expiry check

    def generate_challenge(self, email):
        # Ensure user exists, create if not
        user, created = User.objects.get_or_create(
            username=email,  # Use email as the username
            defaults={'email': email, 'password': 'defaultpassword'}  # Default password if user is created
        )

        # Get or create the EmailOTPDevice instance for the given email
        otp_device, created = EmailOTPDevice.objects.get_or_create(
            email=email,
            defaults={'user': user}  # Associate with the created user if the OTP device is created
        )

        # Generate OTP if it's a new OTP device or if the existing token has expired
        otp_device.token = random_hex(6)  # Generate a 6-character OTP
        otp_device.created_at = now()  # Set creation time
        otp_device.save()

        # Send OTP via email
        subject = "Your One-Time Password (OTP)"
        message = f"Your OTP is: {otp_device.token}. It is valid for 5 minutes."
        email_from = 'your-email@example.com'  # Replace with your verified email address
        send_mail(subject, message, email_from, [otp_device.email])
        
        return True

    def verify_token(self, token):
        if not self.token or not self.created_at:
            return False

        # Check if the OTP has expired (valid for 5 minutes)
        if now() > self.created_at + timedelta(minutes=5):
            return False

        # Verify the token
        return self.token == token