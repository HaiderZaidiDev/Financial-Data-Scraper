from django.db import models
from django import forms

class Ticker(models.Model):
    symbol = models.CharField(max_length = 5)

# Create your models here.
