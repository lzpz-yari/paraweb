"""
Caso de Uso: Crear Usuario - Capa de Aplicación.

Similar a registrar usuario pero permite asignación de rol por administrador.
"""
from datetime import datetime
from application.dtos.usuario_dto import CrearUsuarioDTO, UsuarioDTO
from application.interfaces.repositories import IUsuarioRepository, IRolRepository
from core.entities.usuario import Usuario
from core.value_objects.email import Email
from core.value_objects.password import Password
from core.value_objects.telefono import Telefono
from core.exceptions.usuario_exceptions import (
    UsuarioDuplicadoException,
    RolNoValidoException,
    DatosUsuarioInvalidosException
)


class CrearUsuario:
    """
    Caso de uso para crear un usuario (por administrador).
    
    Similar a RegistrarUsuario pero con permisos administrativos.
    """
    
    def __init__(
        self,
        usuario_repo: IUsuarioRepository,
        rol_repo: IRolRepository,
        password_service
    ):
        """
        Constructor con inyección de dependencias.
        
        Args:
            usuario_repo: Repositorio de usuarios
            rol_repo: Repositorio de roles
            password_service: Servicio de contraseñas
        """
        self.usuario_repo = usuario_repo
        self.rol_repo = rol_repo
        self.password_service = password_service
    
    def execute(self, dto: CrearUsuarioDTO) -> UsuarioDTO:
        """
        Ejecuta la creación del usuario.
        
        Args:
            dto: DTO con datos del nuevo usuario
            
        Returns:
            DTO del usuario creado
        """
        # Validar datos
        self._validar_dto(dto)
        
        # Verificar duplicados
        if self.usuario_repo.existe_email(dto.email):
            raise UsuarioDuplicadoException('email', dto.email)
        
        if self.usuario_repo.existe_username(dto.username):
            raise UsuarioDuplicadoException('username', dto.username)
        
        # Verificar rol
        rol = self.rol_repo.obtener_por_id(dto.rol_id)
        if not rol:
            raise RolNoValidoException(dto.rol_id)
        
        # Encriptar contraseña
        password_hash = self.password_service.encriptar(dto.password)
        
        # Crear entidad
        usuario = Usuario(
            email=dto.email,
            username=dto.username,
            nombre_completo=dto.nombre_completo,
            password_hash=password_hash,
            rol_id=dto.rol_id,
            telefono=dto.telefono,
            is_active=True,
            fecha_registro=datetime.now()
        )
        
        # Guardar
        usuario_guardado = self.usuario_repo.guardar(usuario)
        
        # Retornar DTO
        return self._convertir_a_dto(usuario_guardado, rol.nombre)
    
    def _validar_dto(self, dto: CrearUsuarioDTO) -> None:
        """Valida el DTO de creación."""
        errores = []
        
        try:
            Email(dto.email)
        except ValueError as e:
            errores.append(str(e))
        
        if not dto.username or len(dto.username) < 3:
            errores.append("Username mínimo 3 caracteres")
        
        password_valida, errores_pass = Password.validar(dto.password)
        if not password_valida:
            errores.extend(errores_pass)
        
        if dto.telefono and dto.telefono.strip():
            try:
                Telefono(dto.telefono)
            except ValueError as e:
                errores.append(str(e))
        
        if errores:
            raise DatosUsuarioInvalidosException(errores)
    
    def _convertir_a_dto(self, usuario: Usuario, rol_nombre: str) -> UsuarioDTO:
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
