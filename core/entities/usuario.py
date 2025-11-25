"""
Entidad Usuario - Capa de Dominio.

Entidad pura del negocio sin dependencias externas (sin Django).
Representa un usuario del sistema POS.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List


@dataclass
class Usuario:
    """
    Entidad Usuario del sistema.
    
    Esta entidad representa un usuario con sus datos básicos y reglas de negocio.
    No depende de Django ni de ninguna infraestructura externa.
    
    Attributes:
        id: Identificador único del usuario
        email: Correo electrónico único
        username: Nombre de usuario único
        nombre_completo: Nombre completo del usuario
        telefono: Número de teléfono (opcional)
        password_hash: Hash de la contraseña
        is_active: Si el usuario está activo
        rol_id: ID del rol asignado
        fecha_registro: Fecha de registro en el sistema
        ultimo_acceso: Última fecha de acceso (opcional)
    """
    
    email: str
    username: str
    nombre_completo: str
    password_hash: str
    rol_id: int
    is_active: bool = True
    telefono: Optional[str] = None
    id: Optional[int] = None
    fecha_registro: Optional[datetime] = None
    ultimo_acceso: Optional[datetime] = None
    
    def __post_init__(self):
        """Validaciones básicas al crear la entidad."""
        self._validar_datos_obligatorios()
        self._normalizar_datos()
    
    def _validar_datos_obligatorios(self) -> None:
        """
        Valida que los datos obligatorios estén presentes.
        
        Raises:
            ValueError: Si falta algún dato obligatorio
        """
        if not self.email or not self.email.strip():
            raise ValueError("El email es obligatorio")
        
        if not self.username or not self.username.strip():
            raise ValueError("El username es obligatorio")
        
        if not self.nombre_completo or not self.nombre_completo.strip():
            raise ValueError("El nombre completo es obligatorio")
        
        if not self.password_hash or not self.password_hash.strip():
            raise ValueError("El password hash es obligatorio")
        
        if not isinstance(self.rol_id, int) or self.rol_id <= 0:
            raise ValueError("El rol_id debe ser un entero positivo")
    
    def _normalizar_datos(self) -> None:
        """Normaliza los datos del usuario."""
        self.email = self.email.strip().lower()
        self.username = self.username.strip().lower()
        self.nombre_completo = self.nombre_completo.strip()
        
        if self.telefono:
            self.telefono = self.telefono.strip()
    
    def activar(self) -> None:
        """Activa el usuario."""
        self.is_active = True
    
    def desactivar(self) -> None:
        """Desactiva el usuario (soft delete)."""
        self.is_active = False
    
    def cambiar_rol(self, nuevo_rol_id: int) -> None:
        """
        Cambia el rol del usuario.
        
        Args:
            nuevo_rol_id: ID del nuevo rol
            
        Raises:
            ValueError: Si el rol_id no es válido
        """
        if not isinstance(nuevo_rol_id, int) or nuevo_rol_id <= 0:
            raise ValueError("El rol_id debe ser un entero positivo")
        
        self.rol_id = nuevo_rol_id
    
    def actualizar_ultimo_acceso(self, fecha: datetime) -> None:
        """
        Actualiza la fecha del último acceso.
        
        Args:
            fecha: Fecha y hora del último acceso
        """
        self.ultimo_acceso = fecha
    
    def es_activo(self) -> bool:
        """
        Verifica si el usuario está activo.
        
        Returns:
            True si el usuario está activo, False en caso contrario
        """
        return self.is_active
    
    def __str__(self) -> str:
        """Representación en string del usuario."""
        return f"{self.nombre_completo} ({self.email})"
    
    def __repr__(self) -> str:
        """Representación para debugging."""
        return f"Usuario(id={self.id}, email='{self.email}', username='{self.username}')"
