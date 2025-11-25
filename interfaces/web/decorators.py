"""
Decoradores para autenticación y autorización.

Decoradores personalizados para proteger vistas y verificar permisos.

Principios SOLID:
- Single Responsibility: Cada decorador una validación
- Open/Closed: Extendible mediante composición
"""

from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.http import HttpResponse
from typing import Callable

from application.use_cases.roles.verificar_permiso import VerificarPermiso
from infrastructure.persistence.repositories.permiso_repository import PermisoRepository


def login_required(view_func: Callable) -> Callable:
    """
    Decorador que requiere que el usuario esté autenticado.
    
    Si el usuario no está autenticado, redirige al login.
    
    Args:
        view_func: Vista a proteger
        
    Returns:
        Vista decorada con validación de autenticación
        
    Example:
        @login_required
        def mi_vista(request):
            return HttpResponse("Contenido protegido")
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get('usuario_id'):
            messages.warning(request, 'Debes iniciar sesión para acceder a esta página')
            return redirect('auth:login')
        return view_func(request, *args, **kwargs)
    return wrapper


def permission_required(*codigos_permiso: str) -> Callable:
    """
    Decorador que requiere permisos específicos.
    
    Verifica que el usuario tenga al menos uno de los permisos especificados.
    
    Args:
        *codigos_permiso: Códigos de permisos requeridos (ej: 'usuarios.ver', 'usuarios.crear')
        
    Returns:
        Decorador que valida permisos
        
    Example:
        @login_required
        @permission_required('usuarios.ver', 'usuarios.editar')
        def gestionar_usuarios(request):
            return HttpResponse("Gestión de usuarios")
    """
    def decorator(view_func: Callable) -> Callable:
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Verificar autenticación primero
            usuario_id = request.session.get('usuario_id')
            if not usuario_id:
                messages.warning(request, 'Debes iniciar sesión para acceder')
                return redirect('auth:login')
            
            # Verificar permisos
            verificar_permiso = VerificarPermiso(
                permiso_repository=PermisoRepository()
            )
            
            tiene_permiso = False
            for codigo in codigos_permiso:
                if verificar_permiso.ejecutar(usuario_id, codigo):
                    tiene_permiso = True
                    break
            
            if not tiene_permiso:
                messages.error(
                    request,
                    'No tienes permisos para acceder a esta página'
                )
                return redirect('dashboard')
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def role_required(*nombres_rol: str) -> Callable:
    """
    Decorador que requiere roles específicos.
    
    Verifica que el usuario tenga uno de los roles especificados.
    
    Args:
        *nombres_rol: Nombres de roles requeridos (ej: 'Administrador', 'Gerente')
        
    Returns:
        Decorador que valida roles
        
    Example:
        @login_required
        @role_required('Administrador', 'Gerente')
        def vista_administrativa(request):
            return HttpResponse("Panel administrativo")
    """
    def decorator(view_func: Callable) -> Callable:
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Verificar autenticación
            usuario_id = request.session.get('usuario_id')
            if not usuario_id:
                messages.warning(request, 'Debes iniciar sesión')
                return redirect('auth:login')
            
            # Verificar rol
            rol_usuario = request.session.get('rol_nombre')
            if rol_usuario not in nombres_rol:
                messages.error(
                    request,
                    f'Esta página es solo para: {", ".join(nombres_rol)}'
                )
                return redirect('dashboard')
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def ajax_login_required(view_func: Callable) -> Callable:
    """
    Decorador para vistas AJAX que requieren autenticación.
    
    Retorna JSON con error 401 si no está autenticado.
    
    Args:
        view_func: Vista AJAX a proteger
        
    Returns:
        Vista decorada con validación AJAX
        
    Example:
        @ajax_login_required
        def api_usuarios(request):
            return JsonResponse({'usuarios': [...]})
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get('usuario_id'):
            from django.http import JsonResponse
            return JsonResponse({
                'success': False,
                'message': 'No autenticado'
            }, status=401)
        return view_func(request, *args, **kwargs)
    return wrapper


def superuser_required(view_func: Callable) -> Callable:
    """
    Decorador que solo permite acceso a Administradores.
    
    Args:
        view_func: Vista a proteger
        
    Returns:
        Vista decorada con validación de superusuario
        
    Example:
        @login_required
        @superuser_required
        def panel_administrador(request):
            return HttpResponse("Panel de administrador")
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        usuario_id = request.session.get('usuario_id')
        if not usuario_id:
            messages.warning(request, 'Debes iniciar sesión')
            return redirect('auth:login')
        
        rol_usuario = request.session.get('rol_nombre')
        if rol_usuario != 'Administrador':
            messages.error(
                request,
                'Esta página es solo para administradores'
            )
            return redirect('dashboard')
        
        return view_func(request, *args, **kwargs)
    return wrapper
