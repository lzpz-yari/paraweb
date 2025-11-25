"""
Excepción base del dominio.
"""


class DomainException(Exception):
    """
    Excepción base para todas las excepciones del dominio.
    
    Las excepciones del dominio representan violaciones de reglas
    de negocio y no deben depender de frameworks externos.
    """

    def __init__(self, mensaje: str):
        """
        Inicializa una excepción del dominio.
        
        Args:
            mensaje: Mensaje descriptivo del error
        """
        self.mensaje = mensaje
        super().__init__(self.mensaje)
