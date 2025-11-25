"""
Formularios para cambio y recuperación de contraseña.

Formularios para gestión de contraseñas con validaciones.
"""

from django import forms
from django.core.validators import EmailValidator


class CambioPasswordForm(forms.Form):
    """
    Formulario para cambiar la contraseña del usuario autenticado.
    """
    
    password_actual = forms.CharField(
        max_length=128,
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form__input',
            'placeholder': 'Tu contraseña actual',
            'autocomplete': 'current-password'
        }),
        label='Contraseña Actual',
        error_messages={
            'required': 'La contraseña actual es obligatoria'
        }
    )
    
    password_nueva = forms.CharField(
        min_length=8,
        max_length=128,
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form__input',
            'placeholder': 'Nueva contraseña (mínimo 8 caracteres)',
            'autocomplete': 'new-password'
        }),
        label='Nueva Contraseña',
        error_messages={
            'required': 'La nueva contraseña es obligatoria',
            'min_length': 'La contraseña debe tener al menos 8 caracteres'
        }
    )
    
    password_confirmacion = forms.CharField(
        max_length=128,
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form__input',
            'placeholder': 'Repite la nueva contraseña',
            'autocomplete': 'new-password'
        }),
        label='Confirmar Nueva Contraseña',
        error_messages={
            'required': 'Debes confirmar la nueva contraseña'
        }
    )
    
    def clean(self):
        """
        Validación global del formulario.
        
        Verifica que:
        - Las contraseñas nuevas coincidan
        - La nueva contraseña sea diferente a la actual
        """
        cleaned_data = super().clean()
        password_actual = cleaned_data.get('password_actual')
        password_nueva = cleaned_data.get('password_nueva')
        password_confirmacion = cleaned_data.get('password_confirmacion')
        
        # Verificar que las nuevas contraseñas coincidan
        if password_nueva and password_confirmacion:
            if password_nueva != password_confirmacion:
                raise forms.ValidationError('Las contraseñas nuevas no coinciden')
        
        # Verificar que la nueva sea diferente a la actual
        if password_actual and password_nueva:
            if password_actual == password_nueva:
                raise forms.ValidationError(
                    'La nueva contraseña debe ser diferente a la actual'
                )
        
        return cleaned_data


class RecuperarPasswordForm(forms.Form):
    """
    Formulario para solicitar recuperación de contraseña.
    """
    
    email = forms.EmailField(
        max_length=254,
        required=True,
        validators=[EmailValidator(message='Ingresa un email válido')],
        widget=forms.EmailInput(attrs={
            'class': 'form__input',
            'placeholder': 'tu-email@ejemplo.com',
            'autocomplete': 'email',
            'autofocus': True
        }),
        label='Email',
        error_messages={
            'required': 'El email es obligatorio',
            'invalid': 'Ingresa un email válido'
        }
    )
    
    def clean_email(self):
        """Limpia el email."""
        email = self.cleaned_data.get('email', '').strip().lower()
        
        if not email:
            raise forms.ValidationError('El email no puede estar vacío')
        
        return email


class RestablecerPasswordForm(forms.Form):
    """
    Formulario para restablecer contraseña con token.
    """
    
    password = forms.CharField(
        min_length=8,
        max_length=128,
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form__input',
            'placeholder': 'Nueva contraseña (mínimo 8 caracteres)',
            'autocomplete': 'new-password',
            'autofocus': True
        }),
        label='Nueva Contraseña',
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
            'placeholder': 'Repite tu nueva contraseña',
            'autocomplete': 'new-password'
        }),
        label='Confirmar Contraseña',
        error_messages={
            'required': 'Debes confirmar tu contraseña'
        }
    )
    
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
