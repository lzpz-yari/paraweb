"""
Value Object Telefono - Capa de Dominio.

Objeto de valor inmutable que representa un número telefónico válido.
"""
import re
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Telefono:
    """
    Value Object para Teléfono.
    
    Representa un número telefónico válido e inmutable.
    Soporta formatos de México y formato internacional.
    
    Attributes:
        valor: El número telefónico normalizado
        codigo_pais: Código de país (opcional)
    """
    
    valor: str
    codigo_pais: Optional[str] = "+52"  # México por defecto
    
    # Patrones de validación
    # Formato México: 10 dígitos
    PATRON_MEXICO = re.compile(r'^[0-9]{10}$')
    # Formato internacional: + seguido de 1-3 dígitos (código país) y 7-15 dígitos
    PATRON_INTERNACIONAL = re.compile(r'^\+[0-9]{1,3}[0-9]{7,15}$')
    
    def __post_init__(self):
        """
        Valida el teléfono al crear el objeto.
        
        Raises:
            ValueError: Si el teléfono no es válido
        """
        valor_normalizado = self._normalizar()
        
        # Usamos object.__setattr__ porque el dataclass es frozen
        object.__setattr__(self, 'valor', valor_normalizado)
        
        self._validar()
    
    def _normalizar(self) -> str:
        """
        Normaliza el número telefónico (solo dígitos).
        
        Returns:
            Teléfono normalizado
        """
        if not self.valor:
            return ""
        
        # Remover espacios, guiones, paréntesis
        limpio = re.sub(r'[\s\-\(\)]', '', self.valor.strip())
        
        return limpio
    
    def _validar(self) -> None:
        """
        Valida el formato del teléfono.
        
        Raises:
            ValueError: Si el teléfono no es válido
        """
        if not self.valor:
            raise ValueError("El teléfono no puede estar vacío")
        
        # Verificar si empieza con +
        if self.valor.startswith('+'):
            # Validar formato internacional
            if not self.PATRON_INTERNACIONAL.match(self.valor):
                raise ValueError("El formato internacional del teléfono no es válido (+52XXXXXXXXXX)")
        else:
            # Validar formato México (10 dígitos)
            if not self.PATRON_MEXICO.match(self.valor):
                raise ValueError("El teléfono debe tener 10 dígitos")
            
            # Validar que no empiece con 0 o 1 (en México)
            if self.valor[0] in ['0', '1']:
                raise ValueError("El teléfono no puede empezar con 0 o 1")
    
    def formato_display(self) -> str:
        """
        Formatea el teléfono para mostrar en UI.
        
        Returns:
            Teléfono formateado para mostrar
            
        Example:
            5551234567 -> (555) 123-4567
            +525551234567 -> +52 (555) 123-4567
        """
        if self.valor.startswith('+'):
            # Formato internacional
            codigo = self.valor[0:3]  # +52
            resto = self.valor[3:]
            
            if len(resto) == 10:
                return f"{codigo} ({resto[0:3]}) {resto[3:6]}-{resto[6:]}"
            else:
                return self.valor
        else:
            # Formato México
            if len(self.valor) == 10:
                return f"({self.valor[0:3]}) {self.valor[3:6]}-{self.valor[6:]}"
            else:
                return self.valor
    
    def con_codigo_pais(self) -> str:
        """
        Retorna el teléfono con código de país.
        
        Returns:
            Teléfono con código de país
        """
        if self.valor.startswith('+'):
            return self.valor
        else:
            return f"{self.codigo_pais}{self.valor}"
    
    def es_movil(self) -> bool:
        """
        Verifica si es un número móvil (en México, empieza con ciertos códigos).
        
        Returns:
            True si es móvil, False si no se puede determinar
        """
        if not self.valor.startswith('+'):
            # En México, celulares empiezan con códigos como 55, 33, 81, etc.
            codigos_movil = ['55', '33', '81', '22', '656', '664', '686', '998']
            return any(self.valor.startswith(cod) for cod in codigos_movil)
        return False
    
    def __str__(self) -> str:
        """Representación en string del teléfono."""
        return self.formato_display()
    
    def __repr__(self) -> str:
        """Representación para debugging."""
        return f"Telefono('{self.valor}')"
    
    def __eq__(self, other) -> bool:
        """Compara dos teléfonos."""
        if not isinstance(other, Telefono):
            return False
        return self.valor == other.valor
    
    def __hash__(self) -> int:
        """Hash del teléfono para usar en sets y dicts."""
        return hash(self.valor)
