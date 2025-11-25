"""
Caso de Uso: Actualizar Usuario - Capa de Aplicación.

Implementa la lógica para actualizar datos de un usuario existente.
"""
from application.dtos.usuario_dto import ActualizarUsuarioDTO, UsuarioDTO
from application.interfaces.repositories import IUsuarioRepository, IRolRepository
from core.value_objects.telefono import Telefono
from core.exceptions.usuario_exceptions import (
    UsuarioNoEncontradoException,
    RolNoValidoException,
    DatosUsuarioInvalidosException
)


class ActualizarUsuario:
    """
    Caso de uso para actualizar un usuario existente.
    
    Responsabilidad única: Actualizar datos del usuario.
    """
    
    def __init__(
        self,
        usuario_repo: IUsuarioRepository,
        rol_repo: IRolRepository
    ):
        """
        Constructor con inyección de dependencias.
        
        Args:
            usuario_repo: Repositorio de usuarios
            rol_repo: Repositorio de roles
        """
        self.usuario_repo = usuario_repo
        self.rol_repo = rol_repo
    
    def execute(self, dto: ActualizarUsuarioDTO) -> UsuarioDTO:
        """
        Ejecuta la actualización del usuario.
        
        Args:
            dto: DTO con datos a actualizar
            
        Returns:
            DTO del usuario actualizado
            
        Raises:
            UsuarioNoEncontradoException: Si el usuario no existe
            RolNoValidoException: Si el rol no existe
            DatosUsuarioInvalidosException: Si los datos son inválidos
        """
        # Obtener usuario
        usuario = self.usuario_repo.obtener_por_id(dto.usuario_id)
        if not usuario:
            raise UsuarioNoEncontradoException(str(dto.usuario_id))
        
        # Validar y actualizar campos
        if dto.nombre_completo is not None:
            if len(dto.nombre_completo.strip()) < 3:
                raise DatosUsuarioInvalidosException(
                    ["El nombre completo debe tener al menos 3 caracteres"]
                )
            usuario.nombre_completo = dto.nombre_completo.strip()
        
        if dto.telefono is not None:
            if dto.telefono.strip():
                try:
                    Telefono(dto.telefono)
                except ValueError as e:
                    raise DatosUsuarioInvalidosException([str(e)])
            usuario.telefono = dto.telefono.strip() if dto.telefono.strip() else None
        
        if dto.rol_id is not None:
            rol = self.rol_repo.obtener_por_id(dto.rol_id)
            if not rol:
                raise RolNoValidoException(dto.rol_id)
            usuario.cambiar_rol(dto.rol_id)
        
        if dto.is_active is not None:
            if dto.is_active:
                usuario.activar()
            else:
                usuario.desactivar()
        
        # Guardar cambios
        usuario_actualizado = self.usuario_repo.actualizar(usuario)
        
        # Obtener rol actualizado
        rol = self.rol_repo.obtener_por_id(usuario_actualizado.rol_id)
        
        # Retornar DTO
        return self._convertir_a_dto(usuario_actualizado, rol.nombre if rol else "Sin Rol")
    
    def _convertir_a_dto(self, usuario, rol_nombre: str) -> UsuarioDTO:
        """Convierte entidad a DTO."""
        return UsuarioDTO(
            id=usuario.id,
            email=usuario.email,
            username=usuario.username,
            nombre_completo=usuario.nombre_completo,
            telefono=usuario.telefono,
            rol_id=usuario.rol_id,
            rol_nombre=rol_nombre,
            is_active=usuario.is_active,
            fecha_registro=usuario.fecha_registro,
            ultimo_acceso=usuario.ultimo_acceso
        )
