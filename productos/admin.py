from django.contrib import admin
from django.utils.html import format_html
from .models import Producto, Venta, DetalleVenta


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = [
        'thumbnail_preview',  
        'codigo_barras',
        'nombre',
        'precio_compra',
        'precio_venta',
        'stock',
        'activo',
        'mostrar_ganancia',
        'mostrar_alerta_stock',
    ]
    
    list_filter = [
        'activo',
        'fecha_creacion'
    ]

    search_fields = [
        'codigo_barras',
        'nombre',
        'descripcion'
    ]
    
    list_editable = [
        'stock',
        'activo'
    ]
    
    list_per_page = 30
    ordering = ['nombre']
    
    fieldsets = (
        ('Información Básica', {
            'fields': (
                'codigo_barras',
                'nombre',
                'descripcion',
            )
        }),
        ('Imagen', {
            'fields': (
                'imagen',
                'imagen_preview',
            )
        }),
        ('Precios', {
            'fields': (
                'precio_compra',
                'precio_venta',
            )
        }),
        ('Inventario', {
            'fields': (
                'stock',
                'stock_minimo',
            )
        }),
        ('Estado', {
            'fields': ('activo',),
        }),
        ('Auditoría', {
            'fields': (
                'fecha_creacion',
                'fecha_actualizacion',
            ),
            'classes': ('collapse',), 
        }),
    )

    readonly_fields = [
        'fecha_creacion',
        'fecha_actualizacion',
        'imagen_thumbnail',
        'imagen_preview'
    ]

    @admin.display(description='Imagen')
    def thumbnail_preview(self, obj):
        """Muestra thumbnail en la lista"""
        if obj.imagen_thumbnail:
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 5px;" />',
                obj.get_thumbnail_url()
            )
        return "Sin imagen"
    
    @admin.display(description='Vista Previa')
    def imagen_preview(self, obj):
        """Muestra imagen grande en el formulario"""
        if obj.imagen:
            return format_html(
                '<img src="{}" style="max-width: 300px; max-height: 300px; object-fit: contain; border: 1px solid #ddd; padding: 5px; border-radius: 5px;" />',
                obj.get_imagen_url()
            )
        return "Sin imagen"

    @admin.display(description='Ganancia', ordering='precio_venta')
    def mostrar_ganancia(self, obj):
        ganancia = obj.calcular_ganancia()
        return f"${ganancia:.2f}"

    @admin.display(description='Stock OK', boolean=True)
    def mostrar_alerta_stock(self, obj):
        return not obj.necesita_reordenar()
    
    actions = ['marcar_como_inactivo', 'marcar_como_activo']
    
    @admin.action(description='Marcar como inactivos')
    def marcar_como_inactivo(self, request, queryset):
        updated = queryset.update(activo=False)
        self.message_user(request, f'{updated} producto(s) inactivo(s).') 
    
    @admin.action(description='Marcar como activos')
    def marcar_como_activo(self, request, queryset):
        updated = queryset.update(activo=True)
        self.message_user(request, f'{updated} producto(s) activo(s).')


class DetalleVentaInline(admin.TabularInline):
    model = DetalleVenta 
    extra = 3
    fields = [
        'producto',
        'cantidad',
        'precio_unitario', 
        'subtotal',
    ]
    readonly_fields = ['subtotal']
    autocomplete_fields = ['producto']


@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    inlines = [DetalleVentaInline]
    
    list_display = [
        'id', 
        'fecha', 
        'total', 
        'estado',
        'cantidad_items', 
        'cantidad_productos',
        'ver_ticket',
    ]
    
    list_filter = [
        'estado', 
        'fecha',
    ]
    
    search_fields = [
        'id',
        'notas',
    ]
    
    list_per_page = 25
    ordering = ['-fecha']

    fieldsets = (
        ('Información', {
            'fields': (
                'fecha',
                'estado', 
                'notas',
            )
        }),
        ('Totales', {
            'fields': ('total',),
            'classes': ('collapse',),
        }),
        ('Auditoría', {
            'fields': (
                'fecha_creacion', 
                'fecha_actualizacion',
            ),
            'classes': ('collapse',),
        }),
    )
    
    readonly_fields = [
        'total',
        'fecha_creacion', 
        'fecha_actualizacion',
    ]
    
    actions = ['marcar_completada', 'marcar_cancelada']

    @admin.action(description='Marcar completadas')
    def marcar_completada(self, request, queryset):
        updated = queryset.update(estado='completada')
        self.message_user(request, f'{updated} venta(s) completada(s).')

    @admin.action(description='Marcar canceladas')
    def marcar_cancelada(self, request, queryset):
        updated = queryset.update(estado='cancelada')
        self.message_user(request, f'{updated} venta(s) cancelada(s).')

    @admin.display(description='Ticket')
    def ver_ticket(self, obj):
        from django.urls import reverse
        url = reverse('productos:ticket_venta', args=[obj.id])
        return format_html('<a href="{}"> Ver </a>', url)


@admin.register(DetalleVenta)
class DetalleVentaAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'venta',
        'producto',
        'cantidad',
        'precio_unitario',
        'subtotal',
    ]
    
    list_filter = [
        'venta__fecha',
        'producto',
    ]
    
    search_fields = [
        'venta__id',
        'producto__nombre',
    ]
    
    readonly_fields = ['subtotal']