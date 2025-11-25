"""
Entidad Rol - Capa de Dominio.

Entidad pura del negocio sin dependencias externas.
Representa un rol del sistema con sus permisos asociados.
"""
from dataclasses import dataclass, field
from typing import Optional, List


@dataclass
class Rol:
    """
    Entidad Rol del sistema.
    
    Representa un rol que agrupa permisos y se asigna a usuarios.
    
    Attributes:
        nombre: Nombre del rol
        descripcion: Descripción del rol
        is_active: Si el rol está activo
        is_sistema: Si es un rol del sistema (no editable)
        id: Identificador único del rol
        permisos_ids: Lista de IDs de permisos asociados
    """
    
    nombre: str
    descripcion: str
    is_active: bool = True
    is_sistema: bool = False
    id: Optional[int] = None
    permisos_ids: List[int] = field(default_factory=list)
    
    # Constantes de roles del sistema
    ADMINISTRADOR = "Administrador"
    GERENTE = "Gerente"
    CAJERO = "Cajero"
    MESERO = "Mesero"
    COCINERO = "Cocinero"
    BARTENDER = "Bartender"
    
    ROLES_SISTEMA = [
        ADMINISTRADOR,
        GERENTE,
        CAJERO,
        MESERO,
        COCINERO,
        BARTENDER,
    ]
    
    def __post_init__(self):
        """Validaciones básicas al crear la entidad."""
        self._validar_datos()
        self._normalizar_datos()
    
    def _validar_datos(self) -> None:
        """
        Valida los datos del rol.
        
        Raises:
            ValueError: Si los datos no son válidos
        """
        if not self.nombre or not self.nombre.strip():
            raise ValueError("El nombre del rol es obligatorio")
        
        if len(self.nombre) > 50:
            raise ValueError("El nombre del rol no puede exceder 50 caracteres")
    
    def _normalizar_datos(self) -> None:
        """Normaliza los datos del rol."""
        self.nombre = self.nombre.strip()
        
        if self.descripcion:
            self.descripcion = self.descripcion.strip()
    
    def es_rol_sistema(self) -> bool:
        """
        Verifica si el rol es un rol del sistema.
        
        Returns:
            True si es rol del sistema, False en caso contrario
        """
        return self.is_sistema or self.nombre in self.ROLES_SISTEMA
    
    def activar(self) -> None:
        """Activa el rol."""
        if self.es_rol_sistema():
            raise ValueError("No se puede desactivar un rol del sistema")
        self.is_active = True
    
    def desactivar(self) -> None:
        """
        Desactiva el rol.
        
        Raises:
            ValueError: Si se intenta desactivar un rol del sistema
        """
        if self.es_rol_sistema():
            raise ValueError("No se puede desactivar un rol del sistema")
        self.is_active = False
    
    def agregar_permiso(self, permiso_id: int) -> None:
        """
        Agrega un permiso al rol.
        
        Args:
            permiso_id: ID del permiso a agregar
            
        Raises:
            ValueError: Si el permiso_id no es válido
        """
        if not isinstance(permiso_id, int) or permiso_id <= 0:
            raise ValueError("El permiso_id debe ser un entero positivo")
        
        if permiso_id not in self.permisos_ids:
            self.permisos_ids.append(permiso_id)
    
    def remover_permiso(self, permiso_id: int) -> None:
        """
        Remueve un permiso del rol.
        
        Args:
            permiso_id: ID del permiso a remover
        """
        if permiso_id in self.permisos_ids:
            self.permisos_ids.remove(permiso_id)
    
    def tiene_permiso(self, permiso_id: int) -> bool:
        """
        Verifica si el rol tiene un permiso específico.
        
        Args:
            permiso_id: ID del permiso a verificar
            
        Returns:
            True si tiene el permiso, False en caso contrario
        """
        return permiso_id in self.permisos_ids
    
    def __str__(self) -> str:
        """Representación en string del rol."""
        return self.nombre
    
    def __repr__(self) -> str:
        """Representación para debugging."""
        return f"Rol(id={self.id}, nombre='{self.nombre}', permisos={len(self.permisos_ids)})"
