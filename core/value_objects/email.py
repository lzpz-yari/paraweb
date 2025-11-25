"""
Value Object Email - Capa de Dominio.

Objeto de valor inmutable que representa un email válido.
"""
import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Email:
    """
    Value Object para Email.
    
    Representa un email válido e inmutable.
    Aplica validaciones de formato y normalización.
    
    Attributes:
        valor: El email normalizado
    """
    
    valor: str
    
    # Patrón de validación de email
    PATRON_EMAIL = re.compile(
        r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    )
    
    def __post_init__(self):
        """
        Valida el email al crear el objeto.
        
        Raises:
            ValueError: Si el email no es válido
        """
        email_normalizado = self._normalizar()
        
        # Usamos object.__setattr__ porque el dataclass es frozen
        object.__setattr__(self, 'valor', email_normalizado)
        
        self._validar()
    
    def _normalizar(self) -> str:
        """
        Normaliza el email (lowercase, sin espacios).
        
        Returns:
            Email normalizado
        """
        if not self.valor:
            return ""
        
        return self.valor.strip().lower()
    
    def _validar(self) -> None:
        """
        Valida el formato del email.
        
        Raises:
            ValueError: Si el email no es válido
        """
        if not self.valor:
            raise ValueError("El email no puede estar vacío")
        
        if len(self.valor) > 254:  # RFC 5321
            raise ValueError("El email no puede exceder 254 caracteres")
        
        if not self.PATRON_EMAIL.match(self.valor):
            raise ValueError("El formato del email no es válido")
        
        # Validar partes del email
        partes = self.valor.split('@')
        if len(partes) != 2:
            raise ValueError("El email debe contener exactamente un @")
        
        usuario, dominio = partes
        
        if len(usuario) > 64:  # RFC 5321
            raise ValueError("La parte del usuario no puede exceder 64 caracteres")
        
        if not dominio or '.' not in dominio:
            raise ValueError("El dominio del email no es válido")
    
    def obtener_dominio(self) -> str:
        """
        Obtiene el dominio del email.
        
        Returns:
            El dominio del email
        """
        return self.valor.split('@')[1]
    
    def obtener_usuario(self) -> str:
        """
        Obtiene la parte del usuario del email.
        
        Returns:
            La parte del usuario del email
        """
        return self.valor.split('@')[0]
    
    def __str__(self) -> str:
        """Representación en string del email."""
        return self.valor
    
    def __repr__(self) -> str:
        """Representación para debugging."""
        return f"Email('{self.valor}')"
    
    def __eq__(self, other) -> bool:
        """Compara dos emails."""
        if not isinstance(other, Email):
            return False
        return self.valor == other.valor
    
    def __hash__(self) -> int:
        """Hash del email para usar en sets y dicts."""
        return hash(self.valor)
