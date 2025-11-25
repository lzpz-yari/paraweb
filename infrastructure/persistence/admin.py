"""
Admin configuration para modelos de autenticación.

Registra los modelos en el admin de Django.
"""
from django.contrib import admin
from infrastructure.persistence.models import (
    Usuario,
    Rol,
    Permiso,
    IntentosLogin,
    TokenRecuperacion,
    AuditoriaUsuario
)


@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    """Configuración del admin para Roles."""
    
    list_display = ['nombre', 'descripcion', 'is_active', 'is_sistema', 'fecha_creacion']
    list_filter = ['is_active', 'is_sistema']
    search_fields = ['nombre', 'descripcion']
    filter_horizontal = ['permisos']
    readonly_fields = ['fecha_creacion', 'fecha_modificacion']


@admin.register(Permiso)
class PermisoAdmin(admin.ModelAdmin):
    """Configuración del admin para Permisos."""
    
    list_display = ['nombre', 'codigo', 'modulo', 'fecha_creacion']
    list_filter = ['modulo']
    search_fields = ['nombre', 'codigo', 'descripcion']
    readonly_fields = ['fecha_creacion']


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    """Configuración del admin para Usuarios."""
    
    list_display = ['email', 'username', 'nombre_completo', 'rol', 'is_active', 'fecha_registro']
    list_filter = ['is_active', 'rol', 'fecha_registro']
    search_fields = ['email', 'username', 'nombre_completo']
    readonly_fields = ['fecha_registro', 'ultimo_acceso', 'fecha_modificacion', 'password_hash']
    
    fieldsets = (
        ('Información Personal', {
            'fields': ('email', 'username', 'nombre_completo', 'telefono')
        }),
        ('Rol y Permisos', {
            'fields': ('rol',)
        }),
        ('Estado', {
            'fields': ('is_active',)
        }),
        ('Contraseña', {
            'fields': ('password_hash',),
            'classes': ('collapse',)
        }),
        ('Fechas', {
            'fields': ('fecha_registro', 'ultimo_acceso', 'fecha_modificacion'),
            'classes': ('collapse',)
        }),
    )


@admin.register(IntentosLogin)
class IntentosLoginAdmin(admin.ModelAdmin):
    """Configuración del admin para Intentos de Login."""
    
    list_display = ['identificador', 'exitoso', 'usuario', 'ip_address', 'fecha_intento']
    list_filter = ['exitoso', 'fecha_intento']
    search_fields = ['identificador', 'ip_address']
    readonly_fields = ['usuario', 'identificador', 'exitoso', 'ip_address', 'user_agent', 'fecha_intento']
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


@admin.register(TokenRecuperacion)
class TokenRecuperacionAdmin(admin.ModelAdmin):
    """Configuración del admin para Tokens de Recuperación."""
    
    list_display = ['usuario', 'token', 'fecha_creacion', 'fecha_expiracion', 'usado']
    list_filter = ['usado', 'fecha_creacion']
    search_fields = ['token', 'usuario__email']
    readonly_fields = ['usuario', 'token', 'fecha_creacion', 'fecha_expiracion', 'usado']
    
    def has_add_permission(self, request):
        return False


@admin.register(AuditoriaUsuario)
class AuditoriaUsuarioAdmin(admin.ModelAdmin):
    """Configuración del admin para Auditoría de Usuarios."""
    
    list_display = ['usuario', 'accion', 'usuario_modificador', 'ip_address', 'fecha']
    list_filter = ['accion', 'fecha']
    search_fields = ['usuario__email', 'usuario_modificador__email']
    readonly_fields = ['usuario', 'usuario_modificador', 'accion', 'datos_anteriores', 
                       'datos_nuevos', 'ip_address', 'fecha']
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
