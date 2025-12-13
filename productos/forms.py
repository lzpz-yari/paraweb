from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from .models import Producto, Venta, DetalleVenta


class CustomLoginForm(AuthenticationForm):
    """Formulario de login con validaciones"""
    
    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Usuario',
            'autocomplete': 'username',
            'id': 'id_username'
        }),
        error_messages={
            'required': 'El nombre de usuario es obligatorio',
            'max_length': 'El nombre de usuario no puede exceder 150 caracteres'
        }
    )
    
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Contraseña',
            'autocomplete': 'current-password',
            'id': 'id_password'
        }),
        error_messages={
            'required': 'La contraseña es obligatoria'
        }
    )
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not username:
            raise ValidationError('El nombre de usuario es obligatorio')
        username = username.strip()
        if len(username) < 3:
            raise ValidationError('El nombre de usuario debe tener al menos 3 caracteres')
        return username
    
    def clean_password(self):
        password = self.cleaned_data.get('password')
        if not password:
            raise ValidationError('La contraseña es obligatoria')
        if len(password) < 6:
            raise ValidationError('La contraseña debe tener al menos 6 caracteres')
        return password


class BusquedaProductoForm(forms.Form):
    """Formulario para búsqueda de productos"""
    
    buscar = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'search-input',
            'placeholder': 'Buscar por nombre o código...'
        })
    )
    
    activo = forms.ChoiceField(
        choices=[
            ('', 'Todos los productos'),
            ('1', 'Solo activos'),
            ('0', 'Solo inactivos')
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'filter-select'})
    )
    
    
    def clean_buscar(self):
        buscar = self.cleaned_data.get('buscar', '')
        return buscar.strip()