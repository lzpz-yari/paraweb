"""
DTOs de Login - Capa de Aplicación.

Data Transfer Objects para autenticación.
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class LoginDTO:
    """
    DTO para login de usuario.
    
    Attributes:
        identificador: Email o username
        password: Contraseña en texto plano
        recordar: Si debe recordar la sesión
    """
    identificador: str
    password: str
    recordar: bool = False


@dataclass
class LoginResultDTO:
    """
    DTO con el resultado del login.
    
    Attributes:
        exito: Si el login fue exitoso
        usuario: Datos del usuario (si fue exitoso)
        mensaje: Mensaje de error (si falló)
        token: Token de sesión (opcional)
    """
    exito: bool
    usuario: Optional[object] = None
    mensaje: str = ""
    token: Optional[str] = None


@dataclass
class CambiarPasswordDTO:
    """
    DTO para cambiar contraseña.
    
    Attributes:
        usuario_id: ID del usuario
        password_actual: Contraseña actual
        password_nueva: Nueva contraseña
        password_confirmacion: Confirmación de nueva contraseña
    """
    usuario_id: int
    password_actual: str
    password_nueva: str
    password_confirmacion: str


@dataclass
class RecuperarPasswordDTO:
    """
    DTO para recuperar contraseña.
    
    Attributes:
        email: Email del usuario
    """
    email: str


@dataclass
class RestablecerPasswordDTO:
    """
    DTO para restablecer contraseña con token.
    
    Attributes:
        token: Token de recuperación
        password_nueva: Nueva contraseña
        password_confirmacion: Confirmación de nueva contraseña
    """
    token: str
    password_nueva: str
    password_confirmacion: str
