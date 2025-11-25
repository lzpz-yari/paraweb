"""
Formularios para gestión de usuarios.

Formularios para crear y actualizar usuarios en el sistema.
"""

from django import forms
from django.core.validators import EmailValidator, RegexValidator


class UsuarioCreateForm(forms.Form):
    """
    Formulario para crear un nuevo usuario.
    """
    
    nombre_completo = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form__input',
            'placeholder': 'Nombre completo del usuario'
        }),
        label='Nombre Completo',
        error_messages={
            'required': 'El nombre completo es obligatorio'
        }
    )
    
    email = forms.EmailField(
        max_length=254,
        required=True,
        validators=[EmailValidator()],
        widget=forms.EmailInput(attrs={
            'class': 'form__input',
            'placeholder': 'correo@ejemplo.com'
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
            'placeholder': 'usuario'
        }),
        label='Usuario',
        error_messages={
            'required': 'El usuario es obligatorio'
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
            'placeholder': '5512345678'
        }),
        label='Teléfono (opcional)'
    )
    
    password = forms.CharField(
        min_length=8,
        max_length=128,
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form__input',
            'placeholder': 'Mínimo 8 caracteres'
        }),
        label='Contraseña',
        error_messages={
            'required': 'La contraseña es obligatoria',
            'min_length': 'La contraseña debe tener al menos 8 caracteres'
        }
    )
    
    rol_id = forms.IntegerField(
        required=True,
        widget=forms.Select(attrs={
            'class': 'form__select'
        }),
        label='Rol',
        error_messages={
            'required': 'Debes seleccionar un rol'
        }
    )
    
    def clean_nombre_completo(self):
        """Limpia el nombre completo."""
        nombre = self.cleaned_data.get('nombre_completo', '').strip()
        if len(nombre) < 3:
            raise forms.ValidationError('El nombre debe tener al menos 3 caracteres')
        return nombre
    
    def clean_username(self):
        """Limpia el username."""
        username = self.cleaned_data.get('username', '').strip().lower()
        if len(username) < 3:
            raise forms.ValidationError('El usuario debe tener al menos 3 caracteres')
        return username


class UsuarioUpdateForm(forms.Form):
    """
    Formulario para actualizar un usuario existente.
    
    No incluye email, username ni password ya que no se pueden cambiar
    desde la edición básica.
    """
    
    nombre_completo = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form__input',
            'placeholder': 'Nombre completo del usuario'
        }),
        label='Nombre Completo',
        error_messages={
            'required': 'El nombre completo es obligatorio'
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
            'placeholder': '5512345678'
        }),
        label='Teléfono (opcional)'
    )
    
    rol_id = forms.IntegerField(
        required=True,
        widget=forms.Select(attrs={
            'class': 'form__select'
        }),
        label='Rol',
        error_messages={
            'required': 'Debes seleccionar un rol'
        }
    )
    
    is_active = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form__checkbox'
        }),
        label='Usuario Activo'
    )
    
    def clean_nombre_completo(self):
        """Limpia el nombre completo."""
        nombre = self.cleaned_data.get('nombre_completo', '').strip()
        if len(nombre) < 3:
            raise forms.ValidationError('El nombre debe tener al menos 3 caracteres')
        return nombre
