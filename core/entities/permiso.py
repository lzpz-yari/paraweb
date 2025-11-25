"""
Entidad Permiso - Capa de Dominio.

Entidad pura del negocio sin dependencias externas.
Representa un permiso específico del sistema.
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Permiso:
    """
    Entidad Permiso del sistema.
    
    Representa un permiso granular que puede ser asignado a roles.
    
    Attributes:
        codigo: Código único del permiso (ej: 'ventas.crear')
        nombre: Nombre descriptivo del permiso
        modulo: Módulo al que pertenece el permiso
        descripcion: Descripción detallada del permiso
        id: Identificador único del permiso
    """
    
    codigo: str
    nombre: str
    modulo: str
    descripcion: str = ""
    id: Optional[int] = None
    
    # Módulos del sistema
    MODULO_VENTAS = "ventas"
    MODULO_INVENTARIO = "inventario"
    MODULO_COCINA = "cocina"
    MODULO_REPORTES = "reportes"
    MODULO_CONFIGURACION = "configuracion"
    MODULO_USUARIOS = "usuarios"
    
    MODULOS_VALIDOS = [
        MODULO_VENTAS,
        MODULO_INVENTARIO,
        MODULO_COCINA,
        MODULO_REPORTES,
        MODULO_CONFIGURACION,
        MODULO_USUARIOS,
    ]
    
    # Acciones estándar
    ACCION_VER = "ver"
    ACCION_CREAR = "crear"
    ACCION_EDITAR = "editar"
    ACCION_ELIMINAR = "eliminar"
    ACCION_GESTIONAR = "gestionar"
    
    def __post_init__(self):
        """Validaciones básicas al crear la entidad."""
        self._validar_datos()
        self._normalizar_datos()
    
    def _validar_datos(self) -> None:
        """
        Valida los datos del permiso.
        
        Raises:
            ValueError: Si los datos no son válidos
        """
        if not self.codigo or not self.codigo.strip():
            raise ValueError("El código del permiso es obligatorio")
        
        if not self.nombre or not self.nombre.strip():
            raise ValueError("El nombre del permiso es obligatorio")
        
        if not self.modulo or not self.modulo.strip():
            raise ValueError("El módulo del permiso es obligatorio")
        
        if self.modulo not in self.MODULOS_VALIDOS:
            raise ValueError(f"Módulo inválido. Debe ser uno de: {', '.join(self.MODULOS_VALIDOS)}")
        
        # Validar formato del código (modulo.accion)
        if '.' not in self.codigo:
            raise ValueError("El código debe tener el formato 'modulo.accion'")
        
        partes = self.codigo.split('.')
        if len(partes) != 2:
            raise ValueError("El código debe tener el formato 'modulo.accion'")
    
    def _normalizar_datos(self) -> None:
        """Normaliza los datos del permiso."""
        self.codigo = self.codigo.strip().lower()
        self.nombre = self.nombre.strip()
        self.modulo = self.modulo.strip().lower()
        
        if self.descripcion:
            self.descripcion = self.descripcion.strip()
    
    def obtener_accion(self) -> str:
        """
        Obtiene la acción del código del permiso.
        
        Returns:
            La acción extraída del código (parte después del punto)
        """
        return self.codigo.split('.')[1]
    
    def es_permiso_de_modulo(self, modulo: str) -> bool:
        """
        Verifica si el permiso pertenece a un módulo específico.
        
        Args:
            modulo: Nombre del módulo a verificar
            
        Returns:
            True si pertenece al módulo, False en caso contrario
        """
        return self.modulo.lower() == modulo.lower()
    
    @staticmethod
    def crear_codigo(modulo: str, accion: str) -> str:
        """
        Crea un código de permiso válido.
        
        Args:
            modulo: Módulo del permiso
            accion: Acción del permiso
            
        Returns:
            Código formateado (modulo.accion)
        """
        return f"{modulo.lower()}.{accion.lower()}"
    
    def __str__(self) -> str:
        """Representación en string del permiso."""
        return f"{self.nombre} ({self.codigo})"
    
    def __repr__(self) -> str:
        """Representación para debugging."""
        return f"Permiso(id={self.id}, codigo='{self.codigo}', modulo='{self.modulo}')"
