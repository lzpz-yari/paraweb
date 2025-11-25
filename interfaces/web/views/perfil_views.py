"""
Vistas para gestión de perfil de usuario.

Implementa:
- Vista del perfil del usuario autenticado
- Cambio de contraseña del usuario

Principios SOLID:
- Single Responsibility: Cada vista una funcionalidad
- Dependency Inversion: Inyecta casos de uso
"""

from django.views import View
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator

from application.use_cases.autenticacion.cambiar_password import CambiarPassword
from application.use_cases.usuarios.actualizar_usuario import ActualizarUsuario
from application.dtos.login_dto import CambiarPasswordDTO
from application.dtos.usuario_dto import ActualizarUsuarioDTO
from core.exceptions.auth_exceptions import (
    PasswordActualIncorrectaException,
    PasswordInvalidaException
)
from core.exceptions.usuario_exceptions import (
    UsuarioNoEncontradoException,
    DatosUsuarioInvalidosException
)
from infrastructure.persistence.repositories.usuario_repository import UsuarioRepository
from infrastructure.persistence.repositories.rol_repository import RolRepository
from infrastructure.services.password_service import PasswordService


class PerfilView(View):
    """
    Vista para mostrar y editar el perfil del usuario.
    """
    
    def __init__(self):
        """Inyección de dependencias."""
        self.usuario_repo = UsuarioRepository()
        self.actualizar_usuario = ActualizarUsuario(
            usuario_repo=UsuarioRepository(),
            rol_repo=RolRepository()
        )
    
    def get(self, request: HttpRequest) -> HttpResponse:
        """
        Muestra el perfil del usuario autenticado.
        
        Args:
            request: Objeto HttpRequest
            
        Returns:
            HttpResponse con template del perfil
        """
        # Verificar autenticación
        usuario_id = request.session.get('usuario_id')
        if not usuario_id:
            return redirect('auth:login')
        
        try:
            # Obtener datos del usuario
            usuario = self.usuario_repo.obtener_por_id(usuario_id)
            if not usuario:
                messages.error(request, 'Usuario no encontrado')
                return redirect('auth:login')
            
            return render(request, 'perfil/detalle.html', {
                'usuario': usuario
            })
            
        except UsuarioNoEncontradoException:
            messages.error(request, 'Usuario no encontrado')
            return redirect('auth:login')
        except Exception as e:
            messages.error(request, f'Error al cargar perfil: {str(e)}')
            return redirect('dashboard')
    
    @method_decorator(csrf_protect)
    def post(self, request: HttpRequest) -> HttpResponse:
        """
        Actualiza los datos del perfil.
        
        Args:
            request: Objeto HttpRequest con datos POST
            
        Returns:
            HttpResponse con redirección o errores
        """
        # Verificar autenticación
        usuario_id = request.session.get('usuario_id')
        if not usuario_id:
            return redirect('auth:login')
        
        # Obtener datos del formulario
        nombre_completo = request.POST.get('nombre_completo', '').strip()
        telefono = request.POST.get('telefono', '').strip()
        
        # Validar campos requeridos
        if not nombre_completo:
            messages.error(request, 'El nombre completo es obligatorio')
            return redirect('perfil:detalle')
        
        try:
            # Obtener usuario actual para mantener rol y estado
            usuario_actual = self.usuario_repo.obtener_por_id(usuario_id)
            
            # Crear DTO para el caso de uso
            dto = ActualizarUsuarioDTO(
                nombre_completo=nombre_completo,
                telefono=telefono if telefono else None,
                rol_id=usuario_actual.rol_id,
                is_active=usuario_actual.is_active
            )
            
            # Ejecutar caso de uso
            usuario = self.actualizar_usuario.execute(dto)
            
            # Actualizar datos en sesión
            request.session['usuario_nombre'] = usuario.nombre_completo
            
            messages.success(request, 'Perfil actualizado exitosamente')
            return redirect('perfil:detalle')
            
        except UsuarioNoEncontradoException:
            messages.error(request, 'Usuario no encontrado')
        except DatosUsuarioInvalidosException as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f'Error al actualizar perfil: {str(e)}')
        
        return redirect('perfil:detalle')


@method_decorator(csrf_protect, name='dispatch')
class CambiarPasswordView(View):
    """
    Vista para cambiar la contraseña del usuario.
    """
    
    def __init__(self):
        """Inyección de dependencias."""
        self.cambiar_password = CambiarPassword(
            usuario_repo=UsuarioRepository(),
            password_service=PasswordService()
        )
    
    def get(self, request: HttpRequest) -> HttpResponse:
        """
        Muestra el formulario de cambio de contraseña.
        
        Args:
            request: Objeto HttpRequest
            
        Returns:
            HttpResponse con template del formulario
        """
        # Verificar autenticación
        if not request.session.get('usuario_id'):
            return redirect('auth:login')
        
        return render(request, 'perfil/cambiar_password.html')
    
    def post(self, request: HttpRequest) -> HttpResponse:
        """
        Procesa el cambio de contraseña.
        
        Args:
            request: Objeto HttpRequest con datos POST
            
        Returns:
            HttpResponse con redirección o errores
        """
        # Verificar autenticación
        usuario_id = request.session.get('usuario_id')
        if not usuario_id:
            return redirect('auth:login')
        
        # Obtener datos del formulario
        password_actual = request.POST.get('password_actual', '')
        password_nueva = request.POST.get('password_nueva', '')
        password_confirmacion = request.POST.get('password_confirmacion', '')
        
        # Validar campos requeridos
        if not all([password_actual, password_nueva, password_confirmacion]):
            messages.error(request, 'Todos los campos son obligatorios')
            return render(request, 'perfil/cambiar_password.html')
        
        # Validar que las contraseñas coincidan
        if password_nueva != password_confirmacion:
            messages.error(request, 'Las contraseñas nuevas no coinciden')
            return render(request, 'perfil/cambiar_password.html')
        
        # Validar que la nueva contraseña sea diferente
        if password_actual == password_nueva:
            messages.error(request, 'La nueva contraseña debe ser diferente a la actual')
            return render(request, 'perfil/cambiar_password.html')
        
        try:
            # Crear DTO para el caso de uso
            dto = CambiarPasswordDTO(
                password_actual=password_actual,
                password_nueva=password_nueva
            )
            
            # Ejecutar caso de uso
            self.cambiar_password.execute(dto)
            
            messages.success(request, 'Contraseña actualizada exitosamente')
            return redirect('perfil:detalle')
            
        except PasswordActualIncorrectaException:
            messages.error(request, 'La contraseña actual es incorrecta')
        except PasswordInvalidaException as e:
            messages.error(request, str(e))
        except UsuarioNoEncontradoException:
            messages.error(request, 'Usuario no encontrado')
        except Exception as e:
            messages.error(request, f'Error al cambiar contraseña: {str(e)}')
        
        return render(request, 'perfil/cambiar_password.html')
