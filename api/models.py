from django.db import models
from django.contrib.auth.models import User
import json

# Create your models here.
class profiles(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=50, default='user')
