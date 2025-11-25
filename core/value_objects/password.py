"""
Value Object Password - Capa de Dominio.

Objeto de valor que representa una contraseña con validaciones de fortaleza.
NO almacena el valor en texto plano, solo valida.
"""
import re
from dataclasses import dataclass
from typing import List


@dataclass
class Password:
    """
    Value Object para Password.
    
    Valida la fortaleza de una contraseña.
    NO almacena la contraseña en texto plano.
    
    Attributes:
        errores: Lista de errores de validación encontrados
    """
    
    # Requisitos de contraseña
    LONGITUD_MINIMA = 8
    LONGITUD_MAXIMA = 128
    
    # Patrones de validación
    PATRON_MAYUSCULA = re.compile(r'[A-Z]')
    PATRON_MINUSCULA = re.compile(r'[a-z]')
    PATRON_NUMERO = re.compile(r'\d')
    PATRON_ESPECIAL = re.compile(r'[!@#$%^&*(),.?":{}|<>_\-+=\[\]\\;/]')
    
    # Contraseñas comunes prohibidas (simplificado)
    PASSWORDS_COMUNES = [
        'password', '12345678', 'qwerty123', 'abc12345',
        'password1', 'password123', 'admin123', '11111111',
        'iloveyou', 'welcome1', 'monkey123', 'dragon123',
    ]
    
    @staticmethod
    def validar(password: str) -> tuple[bool, List[str]]:
        """
        Valida la fortaleza de una contraseña.
        
        Args:
            password: Contraseña a validar
            
        Returns:
            Tupla (es_valida, lista_de_errores)
        """
        errores = []
        
        if not password:
            errores.append("La contraseña es obligatoria")
            return False, errores
        
        # Validar longitud
        if len(password) < Password.LONGITUD_MINIMA:
            errores.append(f"La contraseña debe tener al menos {Password.LONGITUD_MINIMA} caracteres")
        
        if len(password) > Password.LONGITUD_MAXIMA:
            errores.append(f"La contraseña no puede exceder {Password.LONGITUD_MAXIMA} caracteres")
        
        # Validar mayúsculas
        if not Password.PATRON_MAYUSCULA.search(password):
            errores.append("La contraseña debe contener al menos una letra mayúscula")
        
        # Validar minúsculas
        if not Password.PATRON_MINUSCULA.search(password):
            errores.append("La contraseña debe contener al menos una letra minúscula")
        
        # Validar números
        if not Password.PATRON_NUMERO.search(password):
            errores.append("La contraseña debe contener al menos un número")
        
        # Validar caracteres especiales
        if not Password.PATRON_ESPECIAL.search(password):
            errores.append("La contraseña debe contener al menos un carácter especial (!@#$%^&*...)")
        
        # Validar contraseñas comunes
        if password.lower() in Password.PASSWORDS_COMUNES:
            errores.append("Esta contraseña es muy común y no es segura")
        
        # Validar secuencias simples
        if Password._tiene_secuencia_simple(password):
            errores.append("La contraseña no debe contener secuencias simples (123, abc, etc.)")
        
        # Validar caracteres repetidos
        if Password._tiene_muchos_repetidos(password):
            errores.append("La contraseña no debe tener muchos caracteres repetidos consecutivos")
        
        es_valida = len(errores) == 0
        return es_valida, errores
    
    @staticmethod
    def _tiene_secuencia_simple(password: str) -> bool:
        """
        Detecta secuencias simples como '123', 'abc', 'xyz'.
        
        Args:
            password: Contraseña a verificar
            
        Returns:
            True si tiene secuencias simples
        """
        password_lower = password.lower()
        
        # Secuencias numéricas
        secuencias_num = ['0123', '1234', '2345', '3456', '4567', '5678', '6789']
        # Secuencias alfabéticas
        secuencias_alpha = ['abcd', 'bcde', 'cdef', 'defg', 'efgh', 'fghi', 
                           'ghij', 'hijk', 'ijkl', 'jklm', 'klmn', 'lmno',
                           'mnop', 'nopq', 'opqr', 'pqrs', 'qrst', 'rstu',
                           'stuv', 'tuvw', 'uvwx', 'vwxy', 'wxyz']
        
        for seq in secuencias_num + secuencias_alpha:
            if seq in password_lower or seq[::-1] in password_lower:
                return True
        
        return False
    
    @staticmethod
    def _tiene_muchos_repetidos(password: str) -> bool:
        """
        Detecta si hay muchos caracteres repetidos consecutivos (3 o más).
        
        Args:
            password: Contraseña a verificar
            
        Returns:
            True si tiene 3 o más caracteres consecutivos iguales
        """
        for i in range(len(password) - 2):
            if password[i] == password[i+1] == password[i+2]:
                return True
        return False
    
    @staticmethod
    def calcular_fortaleza(password: str) -> str:
        """
        Calcula el nivel de fortaleza de la contraseña.
        
        Args:
            password: Contraseña a evaluar
            
        Returns:
            Nivel de fortaleza: 'Débil', 'Media', 'Fuerte', 'Muy Fuerte'
        """
        if not password:
            return "Débil"
        
        puntos = 0
        
        # Longitud
        if len(password) >= 8:
            puntos += 1
        if len(password) >= 12:
            puntos += 1
        if len(password) >= 16:
            puntos += 1
        
        # Complejidad
        if Password.PATRON_MAYUSCULA.search(password):
            puntos += 1
        if Password.PATRON_MINUSCULA.search(password):
            puntos += 1
        if Password.PATRON_NUMERO.search(password):
            puntos += 1
        if Password.PATRON_ESPECIAL.search(password):
            puntos += 1
        
        # Variedad de caracteres
        tipos_chars = 0
        if any(c.isupper() for c in password):
            tipos_chars += 1
        if any(c.islower() for c in password):
            tipos_chars += 1
        if any(c.isdigit() for c in password):
            tipos_chars += 1
        if any(not c.isalnum() for c in password):
            tipos_chars += 1
        
        if tipos_chars >= 4:
            puntos += 1
        
        # Clasificar
        if puntos <= 3:
            return "Débil"
        elif puntos <= 5:
            return "Media"
        elif puntos <= 7:
            return "Fuerte"
        else:
            return "Muy Fuerte"
    
    @staticmethod
    def generar_mensaje_requisitos() -> str:
        """
        Genera un mensaje con los requisitos de contraseña.
        
        Returns:
            Mensaje con los requisitos
        """
        return (
            f"La contraseña debe cumplir los siguientes requisitos:\n"
            f"- Mínimo {Password.LONGITUD_MINIMA} caracteres\n"
            f"- Al menos una letra mayúscula\n"
            f"- Al menos una letra minúscula\n"
            f"- Al menos un número\n"
            f"- Al menos un carácter especial (!@#$%^&*...)\n"
            f"- No debe ser una contraseña común\n"
            f"- No debe contener secuencias simples (123, abc, etc.)"
        )
