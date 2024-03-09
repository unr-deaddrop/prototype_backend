from django.contrib import admin
from .models import Agent, Protocol, Endpoint, Credential, File, Log

# Register your models here.
admin.site.register(Agent)
admin.site.register(Protocol)
admin.site.register(Endpoint)
admin.site.register(Credential)
admin.site.register(File)
admin.site.register(Log)
