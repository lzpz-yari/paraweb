"""
Modelos Django - Capa de Infraestructura.

Modelos de base de datos para autenticación y gestión de usuarios.
"""
from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone


class Rol(models.Model):
    """
    Modelo de Rol del sistema.
    
    Representa un rol que agrupa permisos.
    """
    
    nombre = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Nombre del Rol"
    )
    descripcion = models.TextField(
        blank=True,
        verbose_name="Descripción"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Activo"
    )
    is_sistema = models.BooleanField(
        default=False,
        verbose_name="Rol del Sistema"
    )
    
    # Relación Many-to-Many con Permisos
    permisos = models.ManyToManyField(
        'Permiso',
        related_name='roles',
        blank=True
    )
    
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de Creación"
    )
    fecha_modificacion = models.DateTimeField(
        auto_now=True,
        verbose_name="Fecha de Modificación"
    )
    
    class Meta:
        db_table = 'roles'
        verbose_name = 'Rol'
        verbose_name_plural = 'Roles'
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre


class Permiso(models.Model):
    """
    Modelo de Permiso del sistema.
    
    Representa un permiso granular que puede asignarse a roles.
    """
    
    codigo = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Código del Permiso"
    )
    nombre = models.CharField(
        max_length=100,
        verbose_name="Nombre del Permiso"
    )
    modulo = models.CharField(
        max_length=50,
        verbose_name="Módulo",
        choices=[
            ('ventas', 'Ventas'),
            ('inventario', 'Inventario'),
            ('cocina', 'Cocina'),
            ('reportes', 'Reportes'),
            ('configuracion', 'Configuración'),
            ('usuarios', 'Usuarios'),
        ]
    )
    descripcion = models.TextField(
        blank=True,
        verbose_name="Descripción"
    )
    
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de Creación"
    )
    
    class Meta:
        db_table = 'permisos'
        verbose_name = 'Permiso'
        verbose_name_plural = 'Permisos'
        ordering = ['modulo', 'codigo']
        indexes = [
            models.Index(fields=['codigo']),
            models.Index(fields=['modulo']),
        ]
    
    def __str__(self):
        return f"{self.nombre} ({self.codigo})"


class Usuario(models.Model):
    """
    Modelo de Usuario del sistema.
    
    Representa un usuario con autenticación y rol asignado.
    """
    
    email = models.EmailField(
        unique=True,
        verbose_name="Email",
        db_index=True
    )
    username = models.CharField(
        max_length=150,
        unique=True,
        verbose_name="Username",
        db_index=True
    )
    nombre_completo = models.CharField(
        max_length=200,
        verbose_name="Nombre Completo"
    )
    password_hash = models.CharField(
        max_length=255,
        verbose_name="Password Hash"
    )
    telefono = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Teléfono"
    )
    
    # Relación con Rol
    rol = models.ForeignKey(
        Rol,
        on_delete=models.PROTECT,
        related_name='usuarios',
        verbose_name="Rol"
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name="Activo"
    )
    
    fecha_registro = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de Registro"
    )
    ultimo_acceso = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Último Acceso"
    )
    fecha_modificacion = models.DateTimeField(
        auto_now=True,
        verbose_name="Fecha de Modificación"
    )
    
    class Meta:
        db_table = 'usuarios'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['-fecha_registro']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['username']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.nombre_completo} ({self.email})"
    
    def set_password(self, raw_password: str) -> None:
        """
        Establece la contraseña encriptada.
        
        Args:
            raw_password: Contraseña en texto plano
        """
        self.password_hash = make_password(raw_password)
    
    def check_password(self, raw_password: str) -> bool:
        """
        Verifica la contraseña.
        
        Args:
            raw_password: Contraseña en texto plano
            
        Returns:
            True si la contraseña es correcta
        """
        return check_password(raw_password, self.password_hash)


class IntentosLogin(models.Model):
    """
    Modelo para registrar intentos de login (exitosos y fallidos).
    
    Útil para auditoría y detección de ataques.
    """
    
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='intentos_login',
        verbose_name="Usuario"
    )
    identificador = models.CharField(
        max_length=255,
        verbose_name="Email/Username Intentado"
    )
    exitoso = models.BooleanField(
        default=False,
        verbose_name="Exitoso"
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name="Dirección IP"
    )
    user_agent = models.TextField(
        blank=True,
        verbose_name="User Agent"
    )
    fecha_intento = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha del Intento"
    )
    
    class Meta:
        db_table = 'intentos_login'
        verbose_name = 'Intento de Login'
        verbose_name_plural = 'Intentos de Login'
        ordering = ['-fecha_intento']
        indexes = [
            models.Index(fields=['identificador', 'fecha_intento']),
            models.Index(fields=['exitoso']),
        ]
    
    def __str__(self):
        estado = "Exitoso" if self.exitoso else "Fallido"
        return f"{self.identificador} - {estado} - {self.fecha_intento}"


class TokenRecuperacion(models.Model):
    """
    Modelo para tokens de recuperación de contraseña.
    
    Tokens de un solo uso con expiración.
    """
    
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='tokens_recuperacion',
        verbose_name="Usuario"
    )
    token = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Token",
        db_index=True
    )
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de Creación"
    )
    fecha_expiracion = models.DateTimeField(
        verbose_name="Fecha de Expiración"
    )
    usado = models.BooleanField(
        default=False,
        verbose_name="Usado"
    )
    
    class Meta:
        db_table = 'tokens_recuperacion'
        verbose_name = 'Token de Recuperación'
        verbose_name_plural = 'Tokens de Recuperación'
        ordering = ['-fecha_creacion']
        indexes = [
            models.Index(fields=['token']),
            models.Index(fields=['usado', 'fecha_expiracion']),
        ]
    
    def esta_vigente(self) -> bool:
        """
        Verifica si el token está vigente.
        
        Returns:
            True si el token es válido y no ha expirado
        """
        return (
            not self.usado and
            timezone.now() < self.fecha_expiracion
        )
    
    def __str__(self):
        return f"Token para {self.usuario.email} - {self.fecha_creacion}"


class AuditoriaUsuario(models.Model):
    """
    Modelo para auditoría de cambios en usuarios.
    
    Registra todas las modificaciones importantes.
    """
    
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='auditorias',
        verbose_name="Usuario"
    )
    usuario_modificador = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='auditorias_realizadas',
        verbose_name="Modificado Por"
    )
    accion = models.CharField(
        max_length=50,
        verbose_name="Acción",
        choices=[
            ('crear', 'Crear'),
            ('actualizar', 'Actualizar'),
            ('eliminar', 'Eliminar'),
            ('activar', 'Activar'),
            ('desactivar', 'Desactivar'),
            ('cambiar_rol', 'Cambiar Rol'),
            ('cambiar_password', 'Cambiar Password'),
        ]
    )
    datos_anteriores = models.JSONField(
        null=True,
        blank=True,
        verbose_name="Datos Anteriores"
    )
    datos_nuevos = models.JSONField(
        null=True,
        blank=True,
        verbose_name="Datos Nuevos"
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name="Dirección IP"
    )
    fecha = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha"
    )
    
    class Meta:
        db_table = 'auditoria_usuarios'
        verbose_name = 'Auditoría de Usuario'
        verbose_name_plural = 'Auditorías de Usuarios'
        ordering = ['-fecha']
        indexes = [
            models.Index(fields=['usuario', 'fecha']),
            models.Index(fields=['accion']),
        ]
    
    def __str__(self):
        return f"{self.accion} - {self.usuario.email} - {self.fecha}"
