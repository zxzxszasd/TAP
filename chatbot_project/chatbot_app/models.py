# Create your models here.
from django.db import models

class Message(models.Model):
    sender = models.CharField(max_length=100)
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

class Persona(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
