#Create Serializers here
from rest_framework import serializers
from .models import Example, Account
from django.contrib.auth.models import User

class ExampleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Example
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username']

class AccountSerializer(serializers.ModelSerializer):
    owner = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(),required=True)

    class Meta:
        model = Account
        fields = ['owner','site','title','username','password']