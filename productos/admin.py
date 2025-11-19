from django.contrib import admin
from django.utils.html import format_html
from .models import Producto, Venta, DetalleVenta

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = [
        'codigo_barras',
        'nombre',
        'precio_compra',
        'precio_venta',
        'stock',
        'activo',
        'mostrar_ganancia',
        'mostrar_alerta_stock',
        'mostrar_imagen', 
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
    
    # Creación y edición de productos
    fieldsets = (
        ('Información Básica', {
            'fields': (
                'codigo_barras',
                'nombre',
                'descripcion',
                'imagen',
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
        ('Información de Auditoría', {
            'fields': (
                'fecha_creacion',
                'fecha_actualizacion',
            ),
            'classes': ('collapse',), 
        }),
    )

    readonly_fields = ['fecha_creacion', 'fecha_actualizacion', 'mostrar_miniatura'] 

    @admin.display(description='Ganancia por unidad', ordering='precio_venta')
    def mostrar_ganancia(self, obj):
        ganancia = obj.calcular_ganancia()
        return f"${ganancia:.2f}"

    @admin.display(description='Alerta stock', boolean=True)
    def mostrar_alerta_stock(self, obj):
        return not obj.necesita_reordenar()

    @admin.display(description='Imagen')
    def mostrar_imagen(self, obj):
        if obj.imagen:
            return "Sí"
        return "No"
    
    @admin.display(description='Miniatura')
    def mostrar_miniatura(self, obj):
        if obj.imagen:
            return format_html(
                '<img src="{}" width="200" height="200" style="object-fit: contain;" />',
                obj.imagen.url
            )
        return "Sin imagen"
    
    actions = ['marcar_como_inactivo', 'marcar_como_activo']
    
    @admin.action(description='Marcar productos como inactivos')
    def marcar_como_inactivo(self, request, queryset):
        updated = queryset.update(activo=False)
        self.message_user(request, f'{updated} producto(s) marcado(s) como inactivos.') 
    
    @admin.action(description='Marcar productos como activos')
    def marcar_como_activo(self, request, queryset):
        updated = queryset.update(activo=True)
        self.message_user(request, f'{updated} producto(s) marcado(s) como activos.')


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
        ('Información de la Venta', {
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

    @admin.action(description='Marcar ventas como completadas')
    def marcar_completada(self, request, queryset):
        updated = queryset.update(estado='completada')
        self.message_user(request, f'{updated} venta(s) marcada(s) como completadas.')

    @admin.action(description='Marcar ventas como canceladas')
    def marcar_cancelada(self, request, queryset):
        updated = queryset.update(estado='cancelada')
        self.message_user(request, f'{updated} venta(s) marcada(s) como canceladas.')


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