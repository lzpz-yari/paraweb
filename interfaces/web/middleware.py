"""
Middleware de autenticación.

Middleware personalizado para gestión de sesiones y validación
de autenticación en cada petición.

Principios SOLID:
- Single Responsibility: Solo gestiona autenticación
- Dependency Inversion: Usa repositorios para datos
"""

from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from typing import Callable
from datetime import datetime, timedelta

from infrastructure.persistence.repositories.usuario_repository import UsuarioRepository


class AuthenticationMiddleware:
    """
    Middleware que valida la autenticación en cada petición.
    
    Funcionalidades:
    - Valida sesión activa
    - Verifica expiración de sesión
    - Actualiza último acceso del usuario
    - Permite rutas públicas (login, registro)
    """
    
    # Rutas que no requieren autenticación
    PUBLIC_URLS = [
        '/auth/login',
        '/auth/registro',
        '/auth/recuperar-password',
        '/auth/restablecer-password',
        '/static/',
        '/media/',
    ]
    
    # Tiempo máximo de inactividad (en segundos)
    SESSION_TIMEOUT = 3600  # 1 hora
    
    def __init__(self, get_response: Callable):
        """
        Inicializa el middleware.
        
        Args:
            get_response: Callable que procesa la petición
        """
        self.get_response = get_response
        self.usuario_repository = UsuarioRepository()
    
    def __call__(self, request: HttpRequest) -> HttpResponse:
        """
        Procesa cada petición HTTP.
        
        Args:
            request: Objeto HttpRequest
            
        Returns:
            HttpResponse procesado
        """
        # Verificar si es una ruta pública
        if self._is_public_url(request.path):
            return self.get_response(request)
        
        # Verificar autenticación
        usuario_id = request.session.get('usuario_id')
        
        if not usuario_id:
            # No autenticado, redirigir al login
            messages.warning(request, 'Debes iniciar sesión para continuar')
            return redirect('auth:login')
        
        # Verificar expiración de sesión
        if self._is_session_expired(request):
            # Sesión expirada
            request.session.flush()
            messages.warning(
                request,
                'Tu sesión ha expirado por inactividad. Inicia sesión nuevamente.'
            )
            return redirect('auth:login')
        
        # Verificar que el usuario siga activo
        if not self._is_user_active(usuario_id):
            request.session.flush()
            messages.error(
                request,
                'Tu cuenta ha sido desactivada. Contacta al administrador.'
            )
            return redirect('auth:login')
        
        # Actualizar último acceso
        self._update_last_activity(request)
        
        # Continuar con la petición
        response = self.get_response(request)
        return response
    
    def _is_public_url(self, path: str) -> bool:
        """
        Verifica si una URL es pública.
        
        Args:
            path: Path de la URL
            
        Returns:
            True si la URL es pública
        """
        return any(path.startswith(url) for url in self.PUBLIC_URLS)
    
    def _is_session_expired(self, request: HttpRequest) -> bool:
        """
        Verifica si la sesión ha expirado por inactividad.
        
        Args:
            request: Objeto HttpRequest
            
        Returns:
            True si la sesión expiró
        """
        last_activity = request.session.get('last_activity')
        
        if not last_activity:
            # Primera petición, marcar actividad
            request.session['last_activity'] = datetime.now().isoformat()
            return False
        
        # Calcular tiempo transcurrido
        last_activity_dt = datetime.fromisoformat(last_activity)
        time_elapsed = (datetime.now() - last_activity_dt).total_seconds()
        
        return time_elapsed > self.SESSION_TIMEOUT
    
    def _is_user_active(self, usuario_id: int) -> bool:
        """
        Verifica si el usuario está activo.
        
        Args:
            usuario_id: ID del usuario
            
        Returns:
            True si el usuario está activo
        """
        try:
            usuario = self.usuario_repository.obtener_por_id(usuario_id)
            return usuario is not None and usuario.is_active
        except Exception:
            return False
    
    def _update_last_activity(self, request: HttpRequest) -> None:
        """
        Actualiza la última actividad del usuario.
        
        Args:
            request: Objeto HttpRequest
        """
        request.session['last_activity'] = datetime.now().isoformat()


class SessionSecurityMiddleware:
    """
    Middleware que agrega seguridad adicional a las sesiones.
    
    Funcionalidades:
    - Regenera session ID después del login
    - Valida IP del usuario (opcional)
    - Valida User-Agent (opcional)
    """
    
    def __init__(self, get_response: Callable):
        """Inicializa el middleware."""
        self.get_response = get_response
    
    def __call__(self, request: HttpRequest) -> HttpResponse:
        """
        Procesa cada petición HTTP.
        
        Args:
            request: Objeto HttpRequest
            
        Returns:
            HttpResponse procesado
        """
        # Validaciones de seguridad aquí
        # Por ahora, solo continuar con la petición
        response = self.get_response(request)
        
        # Agregar headers de seguridad
        response['X-Frame-Options'] = 'DENY'
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-XSS-Protection'] = '1; mode=block'
        
        return response
