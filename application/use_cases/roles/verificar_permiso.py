"""
Caso de Uso: Verificar Permiso - Capa de Aplicación.

Implementa la lógica para verificar si un usuario tiene un permiso específico.
"""
from application.interfaces.repositories import IPermisoRepository


class VerificarPermiso:
    """
    Caso de uso para verificar permisos de usuario.
    
    Responsabilidad única: Verificar si un usuario tiene un permiso.
    """
    
    def __init__(self, permiso_repo: IPermisoRepository):
        """
        Constructor con inyección de dependencias.
        
        Args:
            permiso_repo: Repositorio de permisos
        """
        self.permiso_repo = permiso_repo
    
    def execute(self, usuario_id: int, codigo_permiso: str) -> bool:
        """
        Verifica si un usuario tiene un permiso.
        
        Args:
            usuario_id: ID del usuario
            codigo_permiso: Código del permiso (ej: 'ventas.crear')
            
        Returns:
            True si tiene el permiso, False en caso contrario
        """
        return self.permiso_repo.usuario_tiene_permiso(
            usuario_id,
            codigo_permiso
        )
