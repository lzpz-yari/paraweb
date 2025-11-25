"""
Caso de Uso: Cambiar Password - Capa de Aplicación.

Implementa la lógica de cambio de contraseña.
"""
from application.dtos.login_dto import CambiarPasswordDTO
from application.interfaces.repositories import IUsuarioRepository
from core.value_objects.password import Password
from core.exceptions.auth_exceptions import PasswordActualIncorrectaException, PasswordInvalidaException
from core.exceptions.usuario_exceptions import UsuarioNoEncontradoException


class CambiarPassword:
    """
    Caso de uso para cambiar la contraseña de un usuario.
    
    Responsabilidad única: Cambiar contraseña validando la actual.
    """
    
    def __init__(self, usuario_repo: IUsuarioRepository, password_service):
        """
        Constructor con inyección de dependencias.
        
        Args:
            usuario_repo: Repositorio de usuarios
            password_service: Servicio de contraseñas
        """
        self.usuario_repo = usuario_repo
        self.password_service = password_service
    
    def execute(self, dto: CambiarPasswordDTO) -> None:
        """
        Ejecuta el cambio de contraseña.
        
        Args:
            dto: DTO con datos del cambio
            
        Raises:
            UsuarioNoEncontradoException: Si el usuario no existe
            PasswordActualIncorrectaException: Si la contraseña actual es incorrecta
            PasswordInvalidaException: Si la nueva contraseña no es válida
        """
        # Validar que las contraseñas coincidan
        if dto.password_nueva != dto.password_confirmacion:
            raise ValueError("Las contraseñas no coinciden")
        
        # Obtener usuario
        usuario = self.usuario_repo.obtener_por_id(dto.usuario_id)
        if not usuario:
            raise UsuarioNoEncontradoException(str(dto.usuario_id))
        
        # Verificar contraseña actual
        password_actual_valida = self.password_service.verificar(
            dto.password_actual,
            usuario.password_hash
        )
        
        if not password_actual_valida:
            raise PasswordActualIncorrectaException()
        
        # Validar nueva contraseña
        password_valida, errores = Password.validar(dto.password_nueva)
        if not password_valida:
            raise PasswordInvalidaException(errores)
        
        # Encriptar y actualizar
        nuevo_hash = self.password_service.encriptar(dto.password_nueva)
        usuario.password_hash = nuevo_hash
        
        self.usuario_repo.actualizar(usuario)
