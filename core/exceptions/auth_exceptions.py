"""
Excepciones de Autenticación - Capa de Dominio.

Excepciones específicas relacionadas con autenticación y seguridad.
"""
from core.exceptions.base import DomainException


class AuthException(DomainException):
    """Excepción base para errores de autenticación."""
    pass


class CredencialesInvalidasException(AuthException):
    """Excepción cuando las credenciales son inválidas."""
    
    def __init__(self):
        """Constructor."""
        super().__init__("Email o contraseña incorrectos")


class PasswordInvalidaException(AuthException):
    """Excepción cuando la contraseña no cumple los requisitos."""
    
    def __init__(self, errores: list):
        """
        Constructor.
        
        Args:
            errores: Lista de errores de validación de contraseña
        """
        mensaje = "La contraseña no cumple los requisitos: " + "; ".join(errores)
        super().__init__(mensaje)
        self.errores = errores


class PasswordActualIncorrectaException(AuthException):
    """Excepción cuando la contraseña actual es incorrecta."""
    
    def __init__(self):
        """Constructor."""
        super().__init__("La contraseña actual es incorrecta")


class TokenInvalidoException(AuthException):
    """Excepción cuando el token es inválido o expiró."""
    
    def __init__(self, razon: str = "inválido o expirado"):
        """
        Constructor.
        
        Args:
            razon: Razón por la que el token es inválido
        """
        super().__init__(f"El token es {razon}")
        self.razon = razon


class TokenExpiradoException(TokenInvalidoException):
    """Excepción cuando el token ha expirado."""
    
    def __init__(self):
        """Constructor."""
        super().__init__("expirado")


class SesionExpiradaException(AuthException):
    """Excepción cuando la sesión ha expirado."""
    
    def __init__(self):
        """Constructor."""
        super().__init__("La sesión ha expirado. Por favor, inicie sesión nuevamente")


class IntentosLoginExcedidosException(AuthException):
    """Excepción cuando se exceden los intentos de login."""
    
    def __init__(self, minutos_bloqueo: int = 15):
        """
        Constructor.
        
        Args:
            minutos_bloqueo: Minutos que durará el bloqueo
        """
        super().__init__(
            f"Has excedido el número máximo de intentos. "
            f"Intenta nuevamente en {minutos_bloqueo} minutos"
        )
        self.minutos_bloqueo = minutos_bloqueo


class EmailNoVerificadoException(AuthException):
    """Excepción cuando el email no ha sido verificado."""
    
    def __init__(self):
        """Constructor."""
        super().__init__("Debes verificar tu email antes de iniciar sesión")


class OperacionNoAutorizadaException(AuthException):
    """Excepción cuando se intenta una operación no autorizada."""
    
    def __init__(self, operacion: str):
        """
        Constructor.
        
        Args:
            operacion: Descripción de la operación no autorizada
        """
        super().__init__(f"No estás autorizado para: {operacion}")
        self.operacion = operacion
