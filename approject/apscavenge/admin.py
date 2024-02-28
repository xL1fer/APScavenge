from django.contrib import admin
from .models import Seizure, InfoHistory, PasswordHash, AgentStatus#, User

# Register your models here.

admin.site.register(Seizure)
admin.site.register(InfoHistory)
admin.site.register(PasswordHash)
admin.site.register(AgentStatus)
#admin.site.register(User)