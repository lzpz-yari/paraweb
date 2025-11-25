"""
Vistas para gestión de usuarios.

Implementa el CRUD completo de usuarios con:
- Lista paginada con filtros
- Crear nuevo usuario
- Editar usuario existente
- Eliminar usuario (soft delete)

Principios SOLID:
- Single Responsibility: Cada vista una operación CRUD
- Open/Closed: Extendible mediante herencia
- Dependency Inversion: Inyecta casos de uso
"""

from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from django.core.paginator import Paginator
from typing import Optional

from application.use_cases.usuarios.crear_usuario import CrearUsuario
from application.use_cases.usuarios.actualizar_usuario import ActualizarUsuario
from application.use_cases.usuarios.eliminar_usuario import EliminarUsuario
from application.use_cases.usuarios.listar_usuarios import ListarUsuarios
from application.dtos.usuario_dto import CrearUsuarioDTO, ActualizarUsuarioDTO, ListarUsuariosDTO
from core.exceptions.usuario_exceptions import (
    UsuarioNoEncontradoException,
    UsuarioDuplicadoException,
    DatosUsuarioInvalidosException
)
from infrastructure.persistence.repositories.usuario_repository import UsuarioRepository
from infrastructure.persistence.repositories.rol_repository import RolRepository
from infrastructure.services.password_service import PasswordService


class UsuarioListView(View):
    """
    Vista para listar usuarios con paginación y filtros.
    """
    
    def __init__(self):
        """Inyección de dependencias."""
        self.listar_usuarios = ListarUsuarios(
            usuario_repo=UsuarioRepository(),
            rol_repo=RolRepository()
        )
        self.rol_repo = RolRepository()
    
    def get(self, request: HttpRequest) -> HttpResponse:
        """
        Muestra la lista de usuarios.
        
        Args:
            request: Objeto HttpRequest con parámetros GET
            
        Returns:
            HttpResponse con template de lista
        """
        # Verificar autenticación
        if not request.session.get('usuario_id'):
            return redirect('auth:login')
        
        # Obtener parámetros de búsqueda y filtros
        busqueda = request.GET.get('busqueda', '').strip()
        rol_id = request.GET.get('rol_id', '')
        is_active = request.GET.get('is_active', '')
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 10))
        
        # Convertir is_active a booleano si existe
        is_active_bool = None
        if is_active:
            is_active_bool = is_active.lower() == 'true'
        
        try:
            # Crear DTO para el caso de uso
            dto = ListarUsuariosDTO(
                busqueda=busqueda if busqueda else None,
                rol_id=int(rol_id) if rol_id else None,
                is_active=is_active_bool,
                page=page,
                per_page=per_page
            )
            
            # Ejecutar caso de uso
            resultado = self.listar_usuarios.execute(dto)
            
            # Obtener roles para filtros
            roles = self.rol_repository.listar_activos()
            
            context = {
                'usuarios': resultado.usuarios,
                'total': resultado.total,
                'page': resultado.page,
                'per_page': resultado.per_page,
                'total_pages': resultado.total_pages,
                'roles': roles,
                'busqueda': busqueda,
                'rol_id_filtro': rol_id,
                'is_active_filtro': is_active,
            }
            
            return render(request, 'usuarios/lista.html', context)
            
        except Exception as e:
            messages.error(request, f'Error al listar usuarios: {str(e)}')
            return render(request, 'usuarios/lista.html', {
                'usuarios': [],
                'total': 0,
                'roles': []
            })


@method_decorator(csrf_protect, name='dispatch')
class UsuarioCreateView(View):
    """
    Vista para crear un nuevo usuario.
    """
    
    def __init__(self):
        """Inyección de dependencias."""
        self.crear_usuario = CrearUsuario(
            usuario_repo=UsuarioRepository(),
            rol_repo=RolRepository(),
            password_service=PasswordService()
        )
        self.rol_repo = RolRepository()
    
    def get(self, request: HttpRequest) -> HttpResponse:
        """
        Muestra el formulario de creación.
        
        Args:
            request: Objeto HttpRequest
            
        Returns:
            HttpResponse con template del formulario
        """
        # Verificar autenticación
        if not request.session.get('usuario_id'):
            return redirect('auth:login')
        
        # Obtener roles activos
        roles = self.rol_repo.listar_activos()
        
        return render(request, 'usuarios/crear.html', {'roles': roles})
    
    def post(self, request: HttpRequest) -> HttpResponse:
        """
        Procesa la creación de un nuevo usuario.
        
        Args:
            request: Objeto HttpRequest con datos POST
            
        Returns:
            HttpResponse con redirección o errores
        """
        # Verificar autenticación
        if not request.session.get('usuario_id'):
            return redirect('auth:login')
        
        # Obtener datos del formulario
        nombre_completo = request.POST.get('nombre_completo', '').strip()
        email = request.POST.get('email', '').strip()
        username = request.POST.get('username', '').strip()
        telefono = request.POST.get('telefono', '').strip()
        password = request.POST.get('password', '')
        rol_id = request.POST.get('rol_id', '')
        
        # Validar campos requeridos
        if not all([nombre_completo, email, username, password, rol_id]):
            messages.error(request, 'Todos los campos obligatorios deben ser completados')
            return self._render_form(request, locals())
        
        try:
            # Crear DTO para el caso de uso
            dto = CrearUsuarioDTO(
                nombre_completo=nombre_completo,
                email=email,
                username=username,
                telefono=telefono if telefono else None,
                password=password,
                rol_id=int(rol_id)
            )
            
            # Ejecutar caso de uso
            usuario = self.crear_usuario.execute(dto)
            
            messages.success(request, f'Usuario {usuario.nombre_completo} creado exitosamente')
            return redirect('usuarios:lista')
            
        except UsuarioDuplicadoException as e:
            messages.error(request, str(e))
        except DatosUsuarioInvalidosException as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f'Error al crear usuario: {str(e)}')
        
        return self._render_form(request, locals())
    
    def _render_form(self, request: HttpRequest, data: dict) -> HttpResponse:
        """
        Renderiza el formulario con datos previos.
        
        Args:
            request: Objeto HttpRequest
            data: Diccionario con datos del formulario
            
        Returns:
            HttpResponse con template
        """
        roles = self.rol_repo.listar_activos()
        return render(request, 'usuarios/crear.html', {
            'roles': roles,
            'nombre_completo': data.get('nombre_completo', ''),
            'email': data.get('email', ''),
            'username': data.get('username', ''),
            'telefono': data.get('telefono', ''),
            'rol_id': data.get('rol_id', ''),
        })


@method_decorator(csrf_protect, name='dispatch')
class UsuarioUpdateView(View):
    """
    Vista para editar un usuario existente.
    """
    
    def __init__(self):
        """Inyección de dependencias."""
        self.actualizar_usuario = ActualizarUsuario(
            usuario_repo=UsuarioRepository(),
            rol_repo=RolRepository()
        )
        self.usuario_repo = UsuarioRepository()
        self.rol_repo = RolRepository()
    
    def get(self, request: HttpRequest, usuario_id: int) -> HttpResponse:
        """
        Muestra el formulario de edición.
        
        Args:
            request: Objeto HttpRequest
            usuario_id: ID del usuario a editar
            
        Returns:
            HttpResponse con template del formulario
        """
        # Verificar autenticación
        if not request.session.get('usuario_id'):
            return redirect('auth:login')
        
        try:
            # Obtener usuario
            usuario = self.usuario_repo.obtener_por_id(usuario_id)
            if not usuario:
                messages.error(request, 'Usuario no encontrado')
                return redirect('usuarios:lista')
            
            # Obtener roles activos
            roles = self.rol_repository.listar_activos()
            
            return render(request, 'usuarios/editar.html', {
                'usuario': usuario,
                'roles': roles
            })
            
        except UsuarioNoEncontradoException:
            messages.error(request, 'Usuario no encontrado')
            return redirect('usuarios:lista')
        except Exception as e:
            messages.error(request, f'Error al cargar usuario: {str(e)}')
            return redirect('usuarios:lista')
    
    def post(self, request: HttpRequest, usuario_id: int) -> HttpResponse:
        """
        Procesa la actualización del usuario.
        
        Args:
            request: Objeto HttpRequest con datos POST
            usuario_id: ID del usuario a actualizar
            
        Returns:
            HttpResponse con redirección o errores
        """
        # Verificar autenticación
        if not request.session.get('usuario_id'):
            return redirect('auth:login')
        
        # Obtener datos del formulario
        nombre_completo = request.POST.get('nombre_completo', '').strip()
        telefono = request.POST.get('telefono', '').strip()
        rol_id = request.POST.get('rol_id', '')
        is_active = request.POST.get('is_active') == 'on'
        
        # Validar campos requeridos
        if not all([nombre_completo, rol_id]):
            messages.error(request, 'Los campos nombre y rol son obligatorios')
            return redirect('usuarios:editar', usuario_id=usuario_id)
        
        try:
            # Crear DTO para el caso de uso
            dto = ActualizarUsuarioDTO(
                nombre_completo=nombre_completo,
                telefono=telefono if telefono else None,
                rol_id=int(rol_id),
                is_active=is_active
            )
            
            # Ejecutar caso de uso
            usuario = self.actualizar_usuario.execute(dto)
            
            messages.success(request, f'Usuario {usuario.nombre_completo} actualizado exitosamente')
            return redirect('usuarios:lista')
            
        except UsuarioNoEncontradoException:
            messages.error(request, 'Usuario no encontrado')
        except DatosUsuarioInvalidosException as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f'Error al actualizar usuario: {str(e)}')
        
        return redirect('usuarios:editar', usuario_id=usuario_id)


class UsuarioDeleteView(View):
    """
    Vista para eliminar (desactivar) un usuario.
    
    Implementa soft delete, no elimina físicamente el registro.
    """
    
    def __init__(self):
        """Inyección de dependencias."""
        self.eliminar_usuario = EliminarUsuario(
            usuario_repo=UsuarioRepository()
        )
    
    def post(self, request: HttpRequest, usuario_id: int) -> HttpResponse:
        """
        Elimina (desactiva) un usuario.
        
        Args:
            request: Objeto HttpRequest
            usuario_id: ID del usuario a eliminar
            
        Returns:
            JsonResponse con resultado de la operación
        """
        # Verificar autenticación
        if not request.session.get('usuario_id'):
            return JsonResponse({
                'success': False,
                'message': 'No autenticado'
            }, status=401)
        
        try:
            # Ejecutar caso de uso
            self.eliminar_usuario.execute(usuario_id)
            
            return JsonResponse({
                'success': True,
                'message': 'Usuario eliminado exitosamente'
            })
            
        except UsuarioNoEncontradoException:
            return JsonResponse({
                'success': False,
                'message': 'Usuario no encontrado'
            }, status=404)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error al eliminar usuario: {str(e)}'
            }, status=500)
