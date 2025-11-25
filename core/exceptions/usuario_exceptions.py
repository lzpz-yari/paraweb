"""
Excepciones de Usuario - Capa de Dominio.

Excepciones específicas relacionadas con la entidad Usuario.
"""
from core.exceptions.base import DomainException


class UsuarioException(DomainException):
    """Excepción base para errores relacionados con usuarios."""
    pass


class UsuarioNoEncontradoException(UsuarioException):
    """Excepción cuando no se encuentra un usuario."""
    
    def __init__(self, identificador: str):
        """
        Constructor.
        
        Args:
            identificador: Email, username o ID del usuario no encontrado
        """
        super().__init__(f"Usuario no encontrado: {identificador}")
        self.identificador = identificador


class UsuarioDuplicadoException(UsuarioException):
    """Excepción cuando se intenta crear un usuario que ya existe."""
    
    def __init__(self, campo: str, valor: str):
        """
        Constructor.
        
        Args:
            campo: Campo duplicado (email, username)
            valor: Valor del campo duplicado
        """
        super().__init__(f"El {campo} '{valor}' ya está registrado")
        self.campo = campo
        self.valor = valor


class UsuarioInactivoException(UsuarioException):
    """Excepción cuando se intenta operar con un usuario inactivo."""
    
    def __init__(self, identificador: str):
        """
        Constructor.
        
        Args:
            identificador: Email, username o ID del usuario inactivo
        """
        super().__init__(f"El usuario '{identificador}' está inactivo")
        self.identificador = identificador


class UsuarioSinPermisosException(UsuarioException):
    """Excepción cuando un usuario no tiene permisos para una acción."""
    
    def __init__(self, usuario_id: int, accion: str):
        """
        Constructor.
        
        Args:
            usuario_id: ID del usuario sin permisos
            accion: Acción que intentó realizar
        """
        super().__init__(f"El usuario no tiene permisos para: {accion}")
        self.usuario_id = usuario_id
        self.accion = accion


class RolNoValidoException(UsuarioException):
    """Excepción cuando se asigna un rol inválido."""
    
    def __init__(self, rol_id: int):
        """
        Constructor.
        
        Args:
            rol_id: ID del rol inválido
        """
        super().__init__(f"El rol con ID {rol_id} no existe o no es válido")
        self.rol_id = rol_id


class DatosUsuarioInvalidosException(UsuarioException):
    """Excepción cuando los datos del usuario no son válidos."""
    
    def __init__(self, errores: list):
        """
        Constructor.
        
        Args:
            errores: Lista de errores de validación
        """
        mensaje = "Datos del usuario inválidos: " + "; ".join(errores)
        super().__init__(mensaje)
        self.errores = errores
