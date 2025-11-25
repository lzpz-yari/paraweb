"""
Caso de Uso: Registrar Usuario - Capa de Aplicación.

Implementa la lógica de registro de nuevos usuarios.
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


class RegistrarUsuario:
    """
    Caso de uso para registrar un nuevo usuario.
    
    Responsabilidad única: Crear y registrar un usuario nuevo.
    
    Attributes:
        usuario_repo: Repositorio de usuarios
        rol_repo: Repositorio de roles
        password_service: Servicio de encriptación de contraseñas
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
        Ejecuta el caso de uso de registro.
        
        Args:
            dto: DTO con datos del nuevo usuario
            
        Returns:
            DTO del usuario creado
            
        Raises:
            DatosUsuarioInvalidosException: Si los datos son inválidos
            UsuarioDuplicadoException: Si email o username ya existe
            RolNoValidoException: Si el rol no existe
        """
        # Validar datos de entrada
        self._validar_dto(dto)
        
        # Validar que email no exista
        if self.usuario_repo.existe_email(dto.email):
            raise UsuarioDuplicadoException('email', dto.email)
        
        # Validar que username no exista
        if self.usuario_repo.existe_username(dto.username):
            raise UsuarioDuplicadoException('username', dto.username)
        
        # Validar que el rol existe
        rol = self.rol_repo.obtener_por_id(dto.rol_id)
        if not rol:
            raise RolNoValidoException(dto.rol_id)
        
        # Encriptar contraseña
        password_hash = self.password_service.encriptar(dto.password)
        
        # Crear entidad Usuario
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
        
        # Guardar en repositorio
        usuario_guardado = self.usuario_repo.guardar(usuario)
        
        # Convertir a DTO y retornar
        return self._convertir_a_dto(usuario_guardado, rol.nombre)
    
    def _validar_dto(self, dto: CrearUsuarioDTO) -> None:
        """
        Valida el DTO de creación.
        
        Args:
            dto: DTO a validar
            
        Raises:
            DatosUsuarioInvalidosException: Si los datos son inválidos
        """
        errores = []
        
        # Validar email usando Value Object
        try:
            Email(dto.email)
        except ValueError as e:
            errores.append(str(e))
        
        # Validar username
        if not dto.username or len(dto.username) < 3:
            errores.append("El username debe tener al menos 3 caracteres")
        
        if len(dto.username) > 150:
            errores.append("El username no puede exceder 150 caracteres")
        
        # Validar nombre completo
        if not dto.nombre_completo or len(dto.nombre_completo.strip()) < 3:
            errores.append("El nombre completo debe tener al menos 3 caracteres")
        
        # Validar password usando Value Object
        password_valida, errores_password = Password.validar(dto.password)
        if not password_valida:
            errores.extend(errores_password)
        
        # Validar teléfono si está presente
        if dto.telefono and dto.telefono.strip():
            try:
                Telefono(dto.telefono)
            except ValueError as e:
                errores.append(str(e))
        
        if errores:
            raise DatosUsuarioInvalidosException(errores)
    
    def _convertir_a_dto(self, usuario: Usuario, rol_nombre: str) -> UsuarioDTO:
        """
        Convierte entidad Usuario a DTO.
        
        Args:
            usuario: Entidad Usuario
            rol_nombre: Nombre del rol
            
        Returns:
            DTO del usuario
        """
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
