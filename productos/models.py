from django.db import models
from django.utils import timezone
from decimal import Decimal
from .image_utils import (
    process_product_image,
    delete_old_image,
    get_placeholder_url,
    validate_image_size,
    validate_image_format,
    validate_image_dimensions
)


def upload_to_productos(instance, filename):
    """Define ruta de subida organizada por fecha"""
    from datetime import datetime
    now = datetime.now()
    return f'productos/{now.year}/{now.month:02d}/{filename}'


class Producto(models.Model):
    codigo_barras = models.CharField(
        max_length=13,
        unique=True,
        verbose_name="código de barras",
        help_text="código de barras del producto (EAN-13)"
    )
    
    nombre = models.CharField(
        max_length=200,
        verbose_name="nombre del producto",
        help_text="nombre completo del producto"
    )
    
    descripcion = models.TextField(
        blank=True,
        null=True,
        verbose_name="descripción",
        help_text="descripción del producto"
    )
    
    imagen = models.ImageField(
        upload_to=upload_to_productos,
        blank=True,
        null=True,
        verbose_name="imagen del producto",
        help_text="imagen del producto (máx 5MB)",
        validators=[
            validate_image_size,
            validate_image_format,
            validate_image_dimensions
        ]
    )
    
    imagen_thumbnail = models.ImageField(
        upload_to='productos/thumbnails/',
        blank=True,
        null=True,
        verbose_name="miniatura",
        editable=False
    )
    
    precio_compra = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="precio de compra",
        help_text="precio del proveedor"
    )
    
    precio_venta = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="precio de venta",
        help_text="precio para el cliente"
    )
    
    stock = models.PositiveIntegerField(
        default=0,
        verbose_name="stock disponible",
        help_text="cantidad de productos en el inventario"
    )
    
    stock_minimo = models.PositiveIntegerField(
        default=5,
        verbose_name="stock mínimo",
        help_text="cantidad mínima para volver a ordenar"  
    )
    
    activo = models.BooleanField(
        default=True,
        verbose_name="activo",
        help_text="¿sigue disponible para venta?"
    )
    
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name="fecha de creación"
    )
    
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name="fecha de última actualización"
    )

    def __str__(self):
        return f"{self.codigo_barras} - {self.nombre}"
    
    def save(self, *args, **kwargs):
        """Sobrescribir save para procesar imágenes"""
        if self.imagen:
            if self.pk:
                try:
                    old_producto = Producto.objects.get(pk=self.pk)
                    if old_producto.imagen and old_producto.imagen != self.imagen:
                        delete_old_image(old_producto.imagen)
                        delete_old_image(old_producto.imagen_thumbnail)
                except Producto.DoesNotExist:
                    pass
            
            try:
                processed_image, thumbnail = process_product_image(self.imagen)
                self.imagen = processed_image
                self.imagen_thumbnail = thumbnail
            except Exception as e:
                print(f"Error procesando imagen: {e}")
        
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        """Sobrescribir delete para eliminar imágenes físicas"""
        delete_old_image(self.imagen)
        delete_old_image(self.imagen_thumbnail)
        super().delete(*args, **kwargs)
    
    def get_imagen_url(self):
        """Retorna URL de imagen o placeholder"""
        if self.imagen:
            return self.imagen.url
        return get_placeholder_url()
    
    def get_thumbnail_url(self):
        """Retorna URL de thumbnail o placeholder"""
        if self.imagen_thumbnail:
            return self.imagen_thumbnail.url
        elif self.imagen:
            return self.imagen.url
        return get_placeholder_url()
    
    def calcular_ganancia(self):
        return self.precio_venta - self.precio_compra
    
    def necesita_reordenar(self):
        return self.stock <= self.stock_minimo
    
    def tiene_imagen(self):
        return bool(self.imagen)

    class Meta:
        verbose_name = "producto"
        verbose_name_plural = "productos"
        ordering = ['nombre']
        db_table = 'productos_producto'


class Venta(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('completada', 'Completada'),
        ('cancelada', 'Cancelada'),
    ]

    fecha = models.DateTimeField(
        default=timezone.now,
        verbose_name="fecha de venta",
        help_text="fecha y hora de la venta"
    )

    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        verbose_name="subtotal",
        help_text="total sin IVA"
    )

    iva = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        verbose_name="IVA (16%)",
        help_text="impuesto al valor agregado"
    )

    total = models.DecimalField(
        max_digits=10,  
        decimal_places=2,
        default=0.00,
        verbose_name="total de la venta",
        help_text="subtotal + IVA"
    )

    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='pendiente',
        verbose_name="estado",
        help_text="estado de la venta"
    )

    notas = models.TextField(
        blank=True,
        null=True,
        verbose_name="notas",
        help_text="observaciones o notas de la venta"
    )
    
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de Creación"
    )
    
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,  
        verbose_name="Última Actualización"
    )

    def __str__(self):
        return f"Venta #{self.id} - {self.fecha.strftime('%d/%m/%y %H:%M')} - ${self.total}"
    
    def calcular_total(self):
        """Calcula subtotal, IVA y total de la venta"""
        self.subtotal = sum(detalle.subtotal for detalle in self.detalles.all())
        self.iva = self.subtotal * Decimal('0.16')
        self.total = self.subtotal + self.iva
        self.save()
        return self.total
    
    def cantidad_productos(self):
        return sum(detalle.cantidad for detalle in self.detalles.all())
    
    def cantidad_items(self):
        return self.detalles.count()
    
    class Meta:
        verbose_name = "Venta"
        verbose_name_plural = "Ventas"
        ordering = ['-fecha']
        db_table = 'ventas_venta'


class DetalleVenta(models.Model):
    venta = models.ForeignKey(
        Venta,
        on_delete=models.CASCADE,
        related_name='detalles',
        verbose_name="Venta",
        help_text="Venta a la que pertenece este detalle"
    )
    producto = models.ForeignKey(
        Producto,
        on_delete=models.PROTECT,
        related_name='ventas',
        verbose_name="Producto",
        help_text="Producto vendido"
    )
    cantidad = models.PositiveIntegerField(
        default=1,
        verbose_name="Cantidad",
        help_text="Cantidad de unidades vendidas"
    )
    
    precio_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Precio Unitario",
        help_text="Precio por unidad al momento de la venta"
    )
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="subtotal",
        help_text="total de la cantidad por c/u"
    )
    
    def __str__(self):
        return f"{self.cantidad}x {self.producto.nombre} - ${self.subtotal}"
    
    def save(self, *args, **kwargs):
        self.subtotal = self.cantidad * self.precio_unitario
        super().save(*args, **kwargs)
        self.venta.calcular_total()
    
    class Meta:
        verbose_name = "detalle de venta"
        verbose_name_plural = "detalles de la venta"
        db_table = 'ventas_detalleventa'