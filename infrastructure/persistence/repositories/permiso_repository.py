"""
Repositorio de Permiso - Capa de Infraestructura.

Implementación del repositorio de permisos usando Django ORM.
"""
from typing import Optional, List
from infrastructure.persistence.models import Permiso as PermisoModel, Usuario as UsuarioModel
from core.entities.permiso import Permiso


class PermisoRepository:
    """
    Implementación del repositorio de permisos.
    
    Convierte entre modelos Django y entidades del dominio.
    """
    
    def obtener_por_codigo(self, codigo: str) -> Optional[Permiso]:
        """
        Obtiene un permiso por su código.
        
        Args:
            codigo: Código del permiso (ej: 'ventas.crear')
            
        Returns:
            Permiso si existe, None en caso contrario
        """
        try:
            permiso_model = PermisoModel.objects.get(codigo=codigo)
            return self._model_to_entity(permiso_model)
        except PermisoModel.DoesNotExist:
            return None
    
    def listar_por_modulo(self, modulo: str) -> List[Permiso]:
        """
        Lista todos los permisos de un módulo.
        
        Args:
            modulo: Nombre del módulo
            
        Returns:
            Lista de permisos del módulo
        """
        permisos_models = PermisoModel.objects.filter(modulo=modulo)
        
        return [
            self._model_to_entity(permiso_model)
            for permiso_model in permisos_models
        ]
    
    def usuario_tiene_permiso(self, usuario_id: int, codigo_permiso: str) -> bool:
        """
        Verifica si un usuario tiene un permiso específico.
        
        Args:
            usuario_id: ID del usuario
            codigo_permiso: Código del permiso (ej: 'ventas.crear')
            
        Returns:
            True si tiene el permiso, False en caso contrario
        """
        try:
            usuario = UsuarioModel.objects.select_related('rol').prefetch_related(
                'rol__permisos'
            ).get(id=usuario_id)
            
            # Verificar si el usuario está activo
            if not usuario.is_active:
                return False
            
            # Verificar si el rol tiene el permiso
            return usuario.rol.permisos.filter(codigo=codigo_permiso).exists()
            
        except UsuarioModel.DoesNotExist:
            return False
    
    def _model_to_entity(self, permiso_model: PermisoModel) -> Permiso:
        """
        Convierte un modelo Django a entidad del dominio.
        
        Args:
            permiso_model: Modelo Django
            
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
