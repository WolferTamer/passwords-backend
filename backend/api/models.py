from django.db import models
from django.contrib.auth.models import User

# Create your models here. This is where things such as User objects should be defined.
class Example(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    