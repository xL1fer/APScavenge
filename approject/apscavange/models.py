from django.db import models
from django.utils import timezone
from django.db.models.fields.related import OneToOneField

#from django.contrib.auth.models import AbstractUser

# Create your models here.

class Seizure(models.Model):
    email = models.CharField(primary_key=True, max_length=128)

class InfoHistory(models.Model):
    id = models.BigAutoField(primary_key=True)
    user_type = models.CharField(max_length=64, null=True, blank=True)
    user_info = models.TextField(null=True, blank=True)
    capture_time = models.DateTimeField(auto_now_add=True) #(default=timezone.now, auto_now_add=False)
    area = models.CharField(max_length=64, null=True, blank=True)
    seizure_email = models.ForeignKey(Seizure, on_delete=models.CASCADE)

class PasswordHash(models.Model):
    id = models.BigAutoField(primary_key=True)
    asleap = models.CharField(max_length=256, null=True, blank=True)
    jtr = models.CharField(max_length=256, null=True, blank=True)
    hashcat = models.CharField(max_length=256, null=True, blank=True)
    info_history_id = models.OneToOneField(InfoHistory, on_delete=models.CASCADE) # OneToOneField ensures that each "PasswordHash" table entry must be associated to distinct "InfoHistory" entries

#class User(AbstractUser):
#    pass