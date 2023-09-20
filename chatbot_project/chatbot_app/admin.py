from django.contrib import admin

# Register your models here.
from .models import Message
admin.site.register(Message)

# persona
from .models import Persona
admin.site.register(Persona)
