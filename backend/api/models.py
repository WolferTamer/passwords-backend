from django.db import models
from django.contrib.auth.models import User

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