"""
Servicio de Password - Capa de Infraestructura.

Maneja encriptación y verificación de contraseñas usando Django.
"""
from django.contrib.auth.hashers import make_password, check_password
from core.value_objects.password import Password


class PasswordService:
    """
    Servicio para gestión de contraseñas.
    
    Usa el sistema de hashing de Django (PBKDF2 por defecto).
    Responsabilidad única: encriptar y verificar contraseñas.
    """
    
    @staticmethod
    def encriptar(password: str) -> str:
        """
        Encripta una contraseña usando PBKDF2.
        
        Args:
            password: Contraseña en texto plano
            
        Returns:
            Hash de la contraseña
            
        Example:
            >>> service = PasswordService()
            >>> hash = service.encriptar("MiPassword123!")
            >>> hash.startswith('pbkdf2_sha256$')
            True
        """
        if not password:
            raise ValueError("La contraseña no puede estar vacía")
        
        return make_password(password)
    
    @staticmethod
    def verificar(password: str, password_hash: str) -> bool:
        """
        Verifica si una contraseña coincide con un hash.
        
        Args:
            password: Contraseña en texto plano
            password_hash: Hash almacenado
            
        Returns:
            True si la contraseña es correcta
            
        Example:
            >>> service = PasswordService()
            >>> hash = service.encriptar("MiPassword123!")
            >>> service.verificar("MiPassword123!", hash)
            True
            >>> service.verificar("OtraPassword", hash)
            False
        """
        if not password or not password_hash:
            return False
        
        return check_password(password, password_hash)
    
    @staticmethod
    def validar_fortaleza(password: str) -> tuple[bool, list]:
        """
        Valida la fortaleza de una contraseña.
        
        Args:
            password: Contraseña a validar
            
        Returns:
            Tupla (es_valida, lista_errores)
            
        Example:
            >>> service = PasswordService()
            >>> valida, errores = service.validar_fortaleza("123")
            >>> valida
            False
            >>> len(errores) > 0
            True
        """
        return Password.validar(password)
    
    @staticmethod
    def generar_temporal(longitud: int = 12) -> str:
        """
        Genera una contraseña temporal aleatoria.
        
        Args:
            longitud: Longitud de la contraseña (mínimo 8)
            
        Returns:
            Contraseña temporal
        """
        import random
        import string
        
        if longitud < 8:
            longitud = 8
        
        # Asegurar que tenga de todo
        mayusculas = string.ascii_uppercase
        minusculas = string.ascii_lowercase
        digitos = string.digits
        especiales = "!@#$%^&*"
        
        # Garantizar al menos uno de cada tipo
        password_chars = [
            random.choice(mayusculas),
            random.choice(minusculas),
            random.choice(digitos),
            random.choice(especiales)
        ]
        
        # Rellenar el resto
        todos_chars = mayusculas + minusculas + digitos + especiales
        password_chars += random.choices(todos_chars, k=longitud - 4)
        
        # Mezclar
        random.shuffle(password_chars)
        
        return ''.join(password_chars)
