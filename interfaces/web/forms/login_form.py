"""
Formulario de login.

Formulario simple para autenticación de usuarios.
La validación real se hace en el caso de uso LoginUsuario.
"""

from django import forms


class LoginForm(forms.Form):
    """
    Formulario de login.
    
    Campos:
        identificador: Email o username del usuario
        password: Contraseña del usuario
    """
    
    identificador = forms.CharField(
        max_length=254,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form__input',
            'placeholder': 'Email o usuario',
            'autocomplete': 'username',
            'autofocus': True
        }),
        label='Email o Usuario',
        error_messages={
            'required': 'El identificador es obligatorio',
            'max_length': 'El identificador es demasiado largo'
        }
    )
    
    password = forms.CharField(
        max_length=128,
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form__input',
            'placeholder': 'Contraseña',
            'autocomplete': 'current-password'
        }),
        label='Contraseña',
        error_messages={
            'required': 'La contraseña es obligatoria'
        }
    )
    
    def clean_identificador(self):
        """
        Limpia y valida el identificador.
        
        Returns:
            str: Identificador limpio
        """
        identificador = self.cleaned_data.get('identificador', '').strip()
        
        if not identificador:
            raise forms.ValidationError('El identificador no puede estar vacío')
        
        return identificador
