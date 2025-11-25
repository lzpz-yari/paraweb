"""
Caso de Uso: Eliminar Usuario - Capa de Aplicación.

Implementa soft delete de usuarios.
"""
from application.interfaces.repositories import IUsuarioRepository
from core.exceptions.usuario_exceptions import UsuarioNoEncontradoException


class EliminarUsuario:
    """
    Caso de uso para eliminar (desactivar) un usuario.
    
    Implementa soft delete: no borra el registro, solo lo desactiva.
    """
    
    def __init__(self, usuario_repo: IUsuarioRepository):
        """
        Constructor con inyección de dependencias.
        
        Args:
            usuario_repo: Repositorio de usuarios
        """
        self.usuario_repo = usuario_repo
    
    def execute(self, usuario_id: int) -> None:
        """
        Ejecuta la eliminación (soft delete) del usuario.
        
        Args:
            usuario_id: ID del usuario a eliminar
            
        Raises:
            UsuarioNoEncontradoException: Si el usuario no existe
        """
        usuario = self.usuario_repo.obtener_por_id(usuario_id)
        
        if not usuario:
            raise UsuarioNoEncontradoException(str(usuario_id))
        
        # Soft delete
        self.usuario_repo.eliminar(usuario_id)
