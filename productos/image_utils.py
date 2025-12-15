"""
Utilidades para manejo profesional de imágenes de productos
Sistema POS - Buenas prácticas implementadas
"""

from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.exceptions import ValidationError
import os
import sys
import uuid


# CONFIGURACIÓN
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
MIN_WIDTH = 100
MIN_HEIGHT = 100
MAX_WIDTH = 4000
MAX_HEIGHT = 4000

ALLOWED_FORMATS = ['JPEG', 'PNG', 'WEBP']
ALLOWED_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.webp']

THUMBNAIL_SIZE = (150, 150)
LARGE_SIZE = (1200, 1200)


def validate_image_size(image):
    """Valida tamaño del archivo"""
    if image.size > MAX_FILE_SIZE:
        raise ValidationError('Archivo muy grande. Máximo: 5MB')


def validate_image_format(image):
    """Valida formato de imagen"""
    ext = os.path.splitext(image.name)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValidationError(f'Formato no permitido. Use: {", ".join(ALLOWED_EXTENSIONS)}')


def validate_image_dimensions(image):
    """Valida dimensiones de imagen"""
    try:
        img = Image.open(image)
        width, height = img.size
        
        if width < MIN_WIDTH or height < MIN_HEIGHT:
            raise ValidationError(f'Imagen muy pequeña. Mínimo: {MIN_WIDTH}x{MIN_HEIGHT}px')
        
        if width > MAX_WIDTH or height > MAX_HEIGHT:
            raise ValidationError(f'Imagen muy grande. Máximo: {MAX_WIDTH}x{MAX_HEIGHT}px')
        
        img.verify()
    except Exception as e:
        raise ValidationError(f'Imagen inválida: {str(e)}')


def generate_unique_filename(original_filename):
    """Genera nombre único"""
    ext = os.path.splitext(original_filename)[1].lower()
    return f"{uuid.uuid4().hex}{ext}"


def optimize_image(image, quality=85):
    """Optimiza imagen"""
    output = BytesIO()
    
    if image.mode in ('RGBA', 'LA', 'P'):
        background = Image.new('RGB', image.size, (255, 255, 255))
        if image.mode == 'P':
            image = image.convert('RGBA')
        background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
        image = background
    
    image.save(output, format='JPEG', quality=quality, optimize=True)
    output.seek(0)
    return output


def resize_image(image, size):
    """Redimensiona imagen"""
    image_copy = image.copy()
    image_copy.thumbnail(size, Image.Resampling.LANCZOS)
    return image_copy


def create_thumbnail(image_file):
    """Crea thumbnail"""
    img = Image.open(image_file)
    img_thumbnail = resize_image(img, THUMBNAIL_SIZE)
    output = optimize_image(img_thumbnail, quality=80)
    
    original_name = os.path.splitext(image_file.name)[0]
    thumbnail_name = f"{original_name}_thumb.jpg"
    
    return InMemoryUploadedFile(
        output, 'ImageField', thumbnail_name, 'image/jpeg',
        sys.getsizeof(output), None
    )


def process_product_image(image_file):
    """Procesa imagen completa"""
    validate_image_size(image_file)
    validate_image_format(image_file)
    validate_image_dimensions(image_file)
    
    img = Image.open(image_file)
    
    if img.width > LARGE_SIZE[0] or img.height > LARGE_SIZE[1]:
        img = resize_image(img, LARGE_SIZE)
    
    output = optimize_image(img, quality=85)
    unique_name = generate_unique_filename(image_file.name)
    
    processed_file = InMemoryUploadedFile(
        output, 'ImageField', unique_name, 'image/jpeg',
        sys.getsizeof(output), None
    )
    
    image_file.seek(0)
    thumbnail = create_thumbnail(image_file)
    
    return processed_file, thumbnail


def delete_old_image(image_field):
    """Elimina imagen antigua"""
    if image_field:
        try:
            if os.path.isfile(image_field.path):
                os.remove(image_field.path)
        except Exception:
            pass


def get_placeholder_url():
    """URL de placeholder"""
    return '/static/images/no-image-placeholder.png'