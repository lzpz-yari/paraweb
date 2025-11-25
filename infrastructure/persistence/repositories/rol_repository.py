"""
Repositorio de Rol - Capa de Infraestructura.

Implementación del repositorio de roles usando Django ORM.
"""
from typing import Optional, List
from infrastructure.persistence.models import Rol as RolModel, Permiso as PermisoModel
from core.entities.rol import Rol
from core.entities.permiso import Permiso


class RolRepository:
    """
    Implementación del repositorio de roles.
    
    Convierte entre modelos Django y entidades del dominio.
    """
    
    def obtener_por_id(self, rol_id: int) -> Optional[Rol]:
        """
        Obtiene un rol por su ID.
        
        Args:
            rol_id: ID del rol
            
        Returns:
            Rol si existe, None en caso contrario
        """
        try:
            rol_model = RolModel.objects.prefetch_related('permisos').get(id=rol_id)
            return self._model_to_entity(rol_model)
        except RolModel.DoesNotExist:
            return None
    
    def obtener_por_nombre(self, nombre: str) -> Optional[Rol]:
        """
        Obtiene un rol por su nombre.
        
        Args:
            nombre: Nombre del rol
            
        Returns:
            Rol si existe, None en caso contrario
        """
        try:
            rol_model = RolModel.objects.prefetch_related('permisos').get(nombre=nombre)
            return self._model_to_entity(rol_model)
        except RolModel.DoesNotExist:
            return None
    
    def listar_activos(self) -> List[Rol]:
        """
        Lista todos los roles activos.
        
        Returns:
            Lista de roles activos
        """
        roles_models = RolModel.objects.filter(is_active=True).prefetch_related('permisos')
        
        return [
            self._model_to_entity(rol_model)
            for rol_model in roles_models
        ]
    
    def obtener_permisos_de_rol(self, rol_id: int) -> List[Permiso]:
        """
        Obtiene todos los permisos asociados a un rol.
        
        Args:
            rol_id: ID del rol
            
        Returns:
            Lista de permisos del rol
        """
        try:
            rol_model = RolModel.objects.prefetch_related('permisos').get(id=rol_id)
            
            return [
                self._permiso_model_to_entity(permiso_model)
                for permiso_model in rol_model.permisos.all()
            ]
        except RolModel.DoesNotExist:
            return []
    
    def _model_to_entity(self, rol_model: RolModel) -> Rol:
        """
        Convierte un modelo Django a entidad del dominio.
        
        Args:
            rol_model: Modelo Django
            
        Returns:
            Entidad Rol
        """
        # Obtener IDs de permisos
        permisos_ids = list(rol_model.permisos.values_list('id', flat=True))
        
        return Rol(
            id=rol_model.id,
            nombre=rol_model.nombre,
            descripcion=rol_model.descripcion,
            is_active=rol_model.is_active,
            is_sistema=rol_model.is_sistema,
            permisos_ids=permisos_ids
        )
    
    def _permiso_model_to_entity(self, permiso_model: PermisoModel) -> Permiso:
        """
        Convierte un modelo de Permiso Django a entidad.
        
        Args:
            permiso_model: Modelo Django de Permiso
            
        Returns:
            Entidad Permiso
        """
        return Permiso(
            id=permiso_model.id,
            codigo=permiso_model.codigo,
            nombre=permiso_model.nombre,
            modulo=permiso_model.modulo,
            descripcion=permiso_model.descripcion
        )
