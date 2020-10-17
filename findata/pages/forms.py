from django import forms
from django.db import models
from .models import Ticker

class TickerForm(forms.ModelForm):
    class Meta:
        model = Ticker
        fields = ['symbol']
        widgets = {
            'symbol': forms.TextInput(attrs={'placeholder': 'Ex. TSLA', 'required':True})
        }
