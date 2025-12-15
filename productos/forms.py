from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from .models import Producto
from .image_utils import (
    validate_image_size,
    validate_image_format,
    validate_image_dimensions
)


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


class ProductoForm(forms.ModelForm):
    """Formulario de producto con validación de imágenes"""
    
    class Meta:
        model = Producto
        fields = [
            'codigo_barras', 'nombre', 'descripcion',
            'precio_compra', 'precio_venta', 'stock',
            'stock_minimo', 'activo', 'imagen'
        ]
        widgets = {
            'codigo_barras': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Código de barras'
            }),
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del producto'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción'
            }),
            'precio_compra': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.01'
            }),
            'precio_venta': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.01'
            }),
            'stock': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'stock_minimo': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'activo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'imagen': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/jpeg,image/png,image/webp'
            })
        }
    
    def clean_imagen(self):
        """Validación exhaustiva de imagen"""
        imagen = self.cleaned_data.get('imagen')
        
        if not imagen:
            return imagen
        
        try:
            validate_image_size(imagen)
            validate_image_format(imagen)
            validate_image_dimensions(imagen)
        except ValidationError as e:
            raise ValidationError(str(e))
        
        return imagen
    
    def clean_codigo_barras(self):
        """Validación de código de barras"""
        codigo = self.cleaned_data.get('codigo_barras')
        
        if not codigo:
            raise ValidationError('El código de barras es obligatorio')
        
        codigo = codigo.strip()
        
        if len(codigo) < 3:
            raise ValidationError('El código debe tener al menos 3 caracteres')
        
        # Verificar unicidad
        qs = Producto.objects.filter(codigo_barras=codigo)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        
        if qs.exists():
            raise ValidationError('Ya existe un producto con este código')
        
        return codigo
    
    def clean(self):
        """Validación completa del formulario"""
        cleaned_data = super().clean()
        
        precio_compra = cleaned_data.get('precio_compra')
        precio_venta = cleaned_data.get('precio_venta')
        
        if precio_compra and precio_venta:
            if precio_venta <= precio_compra:
                raise ValidationError(
                    'El precio de venta debe ser mayor al de compra'
                )
        
        return cleaned_data
        