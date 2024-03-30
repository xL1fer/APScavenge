from django.db import models
from django.utils import timezone
from django.db.models.fields.related import OneToOneField

from django.core.exceptions import ValidationError

#from django.contrib.auth.models import AbstractUser

# Create your models here.

# NOTE: Field.null (https://docs.djangoproject.com/en/5.0/ref/models/fields/)
#
#   If True, Django will store empty values as NULL in the database. Default is False.
#
#   Avoid using null on string-based fields such as CharField and TextField. If a string-based field has null=True,
#   that means it has two possible values for “no data”: NULL, and the empty string. In most cases, it’s redundant to have two possible values
#   for “no data;” the Django convention is to use the empty string, not NULL. One exception is when a CharField has both
#   unique=True and blank=True set. In this situation, null=True is required to avoid unique constraint violations when saving multiple objects with blank values.
#
#   For both string-based and non-string-based fields, you will also need to set blank=True if you wish to permit empty values in forms,
#   as the null parameter only affects database storage (see blank).
#
#   Basically, null defines if a value can be empty in the database and blank defines if a value can be empty in a form field

def area_validator(value):
    if '_' in value:
        raise ValidationError('Area field must not contain underscore ("_") characters.')

class Seizure(models.Model):
    email = models.CharField(primary_key=True, max_length=128, null=False, blank=False)

class InfoHistory(models.Model):
    id = models.BigAutoField(primary_key=True)
    user_type = models.CharField(max_length=64, blank=True)
    user_info_id = models.BigIntegerField(null=True, blank=True)
    capture_time = models.DateTimeField(auto_now_add=True) #(default=timezone.now, auto_now_add=False)
    area = models.CharField(max_length=64, null=False, blank=False, validators=[area_validator])
    seizure_email = models.ForeignKey(Seizure, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        self.area = self.area.lower()
        super(InfoHistory, self).save(*args, **kwargs)

class PasswordHash(models.Model):
    id = models.BigAutoField(primary_key=True)
    asleap = models.CharField(max_length=256, blank=True)
    jtr = models.CharField(max_length=256, blank=True)
    hashcat = models.CharField(max_length=256, blank=True)
    info_history = models.OneToOneField(InfoHistory, on_delete=models.CASCADE) # OneToOneField ensures that each "PasswordHash" table entry must be associated to distinct "InfoHistory" entries

class AgentStatus(models.Model):
    id = models.BigAutoField(primary_key=True)
    ip = models.CharField(max_length=32, null=False, blank=False)
    token = models.CharField(max_length=128, blank=True)
    area = models.CharField(max_length=64, unique=True, null=False, blank=False, validators=[area_validator])
    alias_name = models.CharField(max_length=64, blank=True)
    is_online = models.BooleanField(default=True)
    is_attacking = models.BooleanField(default=False)
    is_requesting = models.BooleanField(default=False)
    #heartbeat_fails = models.SmallIntegerField(default=0)
    last_heartbeat = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.area = self.area.lower()
        super(AgentStatus, self).save(*args, **kwargs)

#class User(AbstractUser):
#    pass