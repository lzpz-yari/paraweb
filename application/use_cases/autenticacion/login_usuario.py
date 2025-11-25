"""
Caso de Uso: Login de Usuario - Capa de Aplicación.

Implementa la lógica de autenticación de usuarios.
"""
from datetime import datetime
from typing import Optional
from application.dtos.login_dto import LoginDTO, LoginResultDTO
from application.dtos.usuario_dto import UsuarioDTO
from application.interfaces.repositories import IUsuarioRepository, IRolRepository
from core.exceptions.auth_exceptions import (
    CredencialesInvalidasException,
    IntentosLoginExcedidosException
)
from core.exceptions.usuario_exceptions import UsuarioInactivoException


class LoginUsuario:
    """
    Caso de uso para autenticar un usuario.
    
    Responsabilidad única: Validar credenciales y autenticar usuario.
    Aplica principio de Inversión de Dependencias: depende de interfaces,
    no de implementaciones concretas.
    
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
    
    def execute(self, dto: LoginDTO) -> LoginResultDTO:
        """
        Ejecuta el caso de uso de login.
        
        Args:
            dto: DTO con credenciales de login
            
        Returns:
            DTO con resultado del login
            
        Raises:
            CredencialesInvalidasException: Si las credenciales son inválidas
            UsuarioInactivoException: Si el usuario está inactivo
        """
        # Validar datos de entrada
        self._validar_dto(dto)
        
        # Buscar usuario por email o username
        usuario = self._buscar_usuario(dto.identificador)
        
        # Verificar que el usuario exista
        if not usuario:
            raise CredencialesInvalidasException()
        
        # Verificar que el usuario esté activo
        if not usuario.es_activo():
            raise UsuarioInactivoException(dto.identificador)
        
        # Verificar contraseña
        password_valida = self.password_service.verificar(
            dto.password,
            usuario.password_hash
        )
        
        if not password_valida:
            raise CredencialesInvalidasException()
        
        # Actualizar último acceso
        usuario.actualizar_ultimo_acceso(datetime.now())
        self.usuario_repo.actualizar(usuario)
        
        # Obtener rol
        rol = self.rol_repo.obtener_por_id(usuario.rol_id)
        
        # Convertir a DTO
        usuario_dto = self._convertir_a_dto(usuario, rol.nombre if rol else "Sin Rol")
        
        return LoginResultDTO(
            exito=True,
            usuario=usuario_dto,
            mensaje="Login exitoso"
        )
    
    def _validar_dto(self, dto: LoginDTO) -> None:
        """
        Valida el DTO de login.
        
        Args:
            dto: DTO a validar
            
        Raises:
            ValueError: Si los datos son inválidos
        """
        if not dto.identificador or not dto.identificador.strip():
            raise ValueError("El email o username es obligatorio")
        
        if not dto.password or not dto.password.strip():
            raise ValueError("La contraseña es obligatoria")
    
    def _buscar_usuario(self, identificador: str):
        """
        Busca un usuario por email o username.
        
        Args:
            identificador: Email o username
            
        Returns:
            Usuario encontrado o None
        """
        # Intentar primero por email
        if '@' in identificador:
            return self.usuario_repo.obtener_por_email(identificador.lower())
        
        # Intentar por username
        return self.usuario_repo.obtener_por_username(identificador.lower())
    
    def _convertir_a_dto(self, usuario, rol_nombre: str) -> UsuarioDTO:
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
