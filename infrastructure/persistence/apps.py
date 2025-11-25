"""
App Configuration para Infrastructure Persistence.

Configuración de la app Django.
"""
from django.apps import AppConfig


class InfrastructurePersistenceConfig(AppConfig):
    """Configuración de la app de persistencia."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'infrastructure.persistence'
    verbose_name = 'Persistencia (Autenticación y Usuarios)'
