"""
Formulario de registro de usuarios.

Formulario para registro de nuevos usuarios con validación
de campos y coincidencia de contraseñas.
"""

from django import forms
from django.core.validators import EmailValidator, RegexValidator


class RegistroForm(forms.Form):
    """
    Formulario de registro de usuarios.
    """
    
    nombre_completo = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form__input',
            'placeholder': 'Nombre completo',
            'autofocus': True
        }),
        label='Nombre Completo',
        error_messages={
            'required': 'El nombre completo es obligatorio',
            'max_length': 'El nombre es demasiado largo (máximo 255 caracteres)'
        }
    )
    
    email = forms.EmailField(
        max_length=254,
        required=True,
        validators=[EmailValidator(message='Ingresa un email válido')],
        widget=forms.EmailInput(attrs={
            'class': 'form__input',
            'placeholder': 'correo@ejemplo.com',
            'autocomplete': 'email'
        }),
        label='Email',
        error_messages={
            'required': 'El email es obligatorio',
            'invalid': 'Ingresa un email válido'
        }
    )
    
    username = forms.CharField(
        max_length=150,
        required=True,
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z0-9_]+$',
                message='El usuario solo puede contener letras, números y guiones bajos'
            )
        ],
        widget=forms.TextInput(attrs={
            'class': 'form__input',
            'placeholder': 'usuario',
            'autocomplete': 'username'
        }),
        label='Usuario',
        error_messages={
            'required': 'El usuario es obligatorio',
            'max_length': 'El usuario es demasiado largo (máximo 150 caracteres)'
        }
    )
    
    telefono = forms.CharField(
        max_length=10,
        required=False,
        validators=[
            RegexValidator(
                regex=r'^\d{10}$',
                message='El teléfono debe tener 10 dígitos'
            )
        ],
        widget=forms.TextInput(attrs={
            'class': 'form__input',
            'placeholder': '5512345678',
            'autocomplete': 'tel'
        }),
        label='Teléfono (opcional)',
        error_messages={
            'invalid': 'Ingresa un teléfono válido de 10 dígitos'
        }
    )
    
    password = forms.CharField(
        min_length=8,
        max_length=128,
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form__input',
            'placeholder': 'Mínimo 8 caracteres',
            'autocomplete': 'new-password'
        }),
        label='Contraseña',
        error_messages={
            'required': 'La contraseña es obligatoria',
            'min_length': 'La contraseña debe tener al menos 8 caracteres'
        }
    )
    
    password_confirmacion = forms.CharField(
        max_length=128,
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form__input',
            'placeholder': 'Repite tu contraseña',
            'autocomplete': 'new-password'
        }),
        label='Confirmar Contraseña',
        error_messages={
            'required': 'Debes confirmar tu contraseña'
        }
    )
    
    def clean_nombre_completo(self):
        """Limpia el nombre completo."""
        nombre = self.cleaned_data.get('nombre_completo', '').strip()
        
        if not nombre:
            raise forms.ValidationError('El nombre no puede estar vacío')
        
        if len(nombre) < 3:
            raise forms.ValidationError('El nombre debe tener al menos 3 caracteres')
        
        return nombre
    
    def clean_username(self):
        """Limpia el username."""
        username = self.cleaned_data.get('username', '').strip().lower()
        
        if not username:
            raise forms.ValidationError('El usuario no puede estar vacío')
        
        if len(username) < 3:
            raise forms.ValidationError('El usuario debe tener al menos 3 caracteres')
        
        return username
    
    def clean_email(self):
        """Limpia el email."""
        email = self.cleaned_data.get('email', '').strip().lower()
        
        if not email:
            raise forms.ValidationError('El email no puede estar vacío')
        
        return email
    
    def clean(self):
        """
        Validación global del formulario.
        
        Verifica que las contraseñas coincidan.
        """
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirmacion = cleaned_data.get('password_confirmacion')
        
        if password and password_confirmacion:
            if password != password_confirmacion:
                raise forms.ValidationError('Las contraseñas no coinciden')
        
        return cleaned_data
