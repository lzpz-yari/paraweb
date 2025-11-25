"""
Servicio de Token - Capa de Infraestructura.

Genera y valida tokens de recuperación de contraseña.
"""
import secrets
from datetime import datetime, timedelta
from django.utils import timezone


class TokenService:
    """
    Servicio para gestión de tokens.
    
    Genera tokens únicos y seguros para recuperación de contraseña.
    Responsabilidad única: crear y validar tokens.
    """
    
    # Tiempo de validez del token (en horas)
    VALIDEZ_HORAS = 1
    
    @staticmethod
    def generar_token() -> str:
        """
        Genera un token único y seguro.
        
        Returns:
            Token aleatorio de 32 bytes en hexadecimal
            
        Example:
            >>> service = TokenService()
            >>> token = service.generar_token()
            >>> len(token)
            64
        """
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def calcular_expiracion(horas: int = None) -> datetime:
        """
        Calcula la fecha de expiración del token.
        
        Args:
            horas: Horas de validez (por defecto usa VALIDEZ_HORAS)
            
        Returns:
            Fecha de expiración
            
        Example:
            >>> service = TokenService()
            >>> expiracion = service.calcular_expiracion(1)
            >>> expiracion > timezone.now()
            True
        """
        if horas is None:
            horas = TokenService.VALIDEZ_HORAS
        
        return timezone.now() + timedelta(hours=horas)
    
    @staticmethod
    def token_esta_vigente(fecha_expiracion: datetime, usado: bool) -> bool:
        """
        Verifica si un token está vigente.
        
        Args:
            fecha_expiracion: Fecha de expiración del token
            usado: Si el token ya fue usado
            
        Returns:
            True si el token es válido
            
        Example:
            >>> from django.utils import timezone
            >>> from datetime import timedelta
            >>> service = TokenService()
            >>> expiracion = timezone.now() + timedelta(hours=1)
            >>> service.token_esta_vigente(expiracion, False)
            True
            >>> service.token_esta_vigente(expiracion, True)
            False
        """
        return not usado and timezone.now() < fecha_expiracion
