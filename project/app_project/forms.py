from django import forms
from .models import *
from .forms import *

class BookForm(forms.ModelForm):
    class Meta:
        model = book
        fields = '__all__'
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'author': forms.TextInput(attrs={'class': 'form-control'}),
            'photo_book': forms.FileInput(attrs={'class': 'form-control'}),
            'photo_author': forms.FileInput(attrs={'class': 'form-control'}),
            'pages': forms.NumberInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'rental_price_day': forms.NumberInput(attrs={'class': 'form-control', 'id':'rental_price_day'}),
            'rental_period': forms.NumberInput(attrs={'class': 'form-control', 'id':'rental_period'}),
            'total_rental_price': forms.NumberInput(attrs={'class': 'form-control' , 'id':'total_rental_price'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
        }

class CategoryForm(forms.ModelForm):
    class Meta:
        model = categories
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }