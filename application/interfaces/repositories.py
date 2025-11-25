"""
Interfaces de Repositorios - Capa de Aplicación.

Contratos que deben implementar los repositorios de infraestructura.
Usa typing.Protocol para definir interfaces sin herencia.
"""
from typing import Protocol, Optional, List
from datetime import datetime
from core.entities.usuario import Usuario
from core.entities.rol import Rol
from core.entities.permiso import Permiso


class IUsuarioRepository(Protocol):
    """
    Interfaz del repositorio de usuarios.
    
    Define el contrato que debe cumplir cualquier implementación
    del repositorio de usuarios.
    """
    
    def guardar(self, usuario: Usuario) -> Usuario:
        """
        Guarda un usuario nuevo.
        
        Args:
            usuario: Entidad Usuario a guardar
            
        Returns:
            Usuario guardado con ID asignado
            
        Raises:
            UsuarioDuplicadoException: Si el email o username ya existe
        """
        ...
    
    def actualizar(self, usuario: Usuario) -> Usuario:
        """
        Actualiza un usuario existente.
        
        Args:
            usuario: Entidad Usuario a actualizar
            
        Returns:
            Usuario actualizado
            
        Raises:
            UsuarioNoEncontradoException: Si el usuario no existe
        """
        ...
    
    def obtener_por_id(self, usuario_id: int) -> Optional[Usuario]:
        """
        Obtiene un usuario por su ID.
        
        Args:
            usuario_id: ID del usuario
            
        Returns:
            Usuario si existe, None en caso contrario
        """
        ...
    
    def obtener_por_email(self, email: str) -> Optional[Usuario]:
        """
        Obtiene un usuario por su email.
        
        Args:
            email: Email del usuario
            
        Returns:
            Usuario si existe, None en caso contrario
        """
        ...
    
    def obtener_por_username(self, username: str) -> Optional[Usuario]:
        """
        Obtiene un usuario por su username.
        
        Args:
            username: Username del usuario
            
        Returns:
            Usuario si existe, None en caso contrario
        """
        ...
    
    def existe_email(self, email: str, excluir_id: Optional[int] = None) -> bool:
        """
        Verifica si existe un email.
        
        Args:
            email: Email a verificar
            excluir_id: ID de usuario a excluir de la búsqueda
            
        Returns:
            True si existe, False en caso contrario
        """
        ...
    
    def existe_username(self, username: str, excluir_id: Optional[int] = None) -> bool:
        """
        Verifica si existe un username.
        
        Args:
            username: Username a verificar
            excluir_id: ID de usuario a excluir de la búsqueda
            
        Returns:
            True si existe, False en caso contrario
        """
        ...
    
    def listar(
        self,
        busqueda: Optional[str] = None,
        rol_id: Optional[int] = None,
        is_active: Optional[bool] = None,
        limite: int = 20,
        offset: int = 0
    ) -> List[Usuario]:
        """
        Lista usuarios con filtros.
        
        Args:
            busqueda: Texto de búsqueda en email, username, nombre
            rol_id: Filtrar por rol
            is_active: Filtrar por estado
            limite: Máximo de registros
            offset: Offset para paginación
            
        Returns:
            Lista de usuarios que coinciden con los filtros
        """
        ...
    
    def contar(
        self,
        busqueda: Optional[str] = None,
        rol_id: Optional[int] = None,
        is_active: Optional[bool] = None
    ) -> int:
        """
        Cuenta usuarios con filtros.
        
        Args:
            busqueda: Texto de búsqueda en email, username, nombre
            rol_id: Filtrar por rol
            is_active: Filtrar por estado
            
        Returns:
            Número de usuarios que coinciden con los filtros
        """
        ...
    
    def eliminar(self, usuario_id: int) -> None:
        """
        Elimina (soft delete) un usuario.
        
        Args:
            usuario_id: ID del usuario a eliminar
            
        Raises:
            UsuarioNoEncontradoException: Si el usuario no existe
        """
        ...


class IRolRepository(Protocol):
    """
    Interfaz del repositorio de roles.
    
    Define el contrato que debe cumplir cualquier implementación
    del repositorio de roles.
    """
    
    def obtener_por_id(self, rol_id: int) -> Optional[Rol]:
        """
        Obtiene un rol por su ID.
        
        Args:
            rol_id: ID del rol
            
        Returns:
            Rol si existe, None en caso contrario
        """
        ...
    
    def obtener_por_nombre(self, nombre: str) -> Optional[Rol]:
        """
        Obtiene un rol por su nombre.
        
        Args:
            nombre: Nombre del rol
            
        Returns:
            Rol si existe, None en caso contrario
        """
        ...
    
    def listar_activos(self) -> List[Rol]:
        """
        Lista todos los roles activos.
        
        Returns:
            Lista de roles activos
        """
        ...
    
    def obtener_permisos_de_rol(self, rol_id: int) -> List[Permiso]:
        """
        Obtiene todos los permisos asociados a un rol.
        
        Args:
            rol_id: ID del rol
            
        Returns:
            Lista de permisos del rol
        """
        ...


class IPermisoRepository(Protocol):
    """
    Interfaz del repositorio de permisos.
    
    Define el contrato que debe cumplir cualquier implementación
    del repositorio de permisos.
    """
    
    def obtener_por_codigo(self, codigo: str) -> Optional[Permiso]:
        """
        Obtiene un permiso por su código.
        
        Args:
            codigo: Código del permiso (ej: 'ventas.crear')
            
        Returns:
            Permiso si existe, None en caso contrario
        """
        ...
    
    def listar_por_modulo(self, modulo: str) -> List[Permiso]:
        """
        Lista todos los permisos de un módulo.
        
        Args:
            modulo: Nombre del módulo
            
        Returns:
            Lista de permisos del módulo
        """
        ...
    
    def usuario_tiene_permiso(self, usuario_id: int, codigo_permiso: str) -> bool:
        """
        Verifica si un usuario tiene un permiso específico.
        
        Args:
            usuario_id: ID del usuario
            codigo_permiso: Código del permiso (ej: 'ventas.crear')
            
        Returns:
            True si tiene el permiso, False en caso contrario
        """
        ...
