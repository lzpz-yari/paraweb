"""
Vistas de autenticación.

Implementa las vistas para el flujo de autenticación:
- Login de usuarios
- Logout
- Registro de nuevos usuarios
- Recuperación y restablecimiento de contraseña

Principios SOLID aplicados:
- Single Responsibility: Cada vista maneja una funcionalidad específica
- Dependency Inversion: Depende de casos de uso (abstracciones)
"""

from django.views import View
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from typing import Optional

from application.use_cases.autenticacion.login_usuario import LoginUsuario
from application.use_cases.autenticacion.registrar_usuario import RegistrarUsuario
from application.dtos.login_dto import LoginDTO, RecuperarPasswordDTO, RestablecerPasswordDTO
from application.dtos.usuario_dto import CrearUsuarioDTO
from core.exceptions.auth_exceptions import (
    CredencialesInvalidasException,
    PasswordInvalidaException,
    TokenInvalidoException,
    TokenExpiradoException,
    IntentosLoginExcedidosException
)
from core.exceptions.usuario_exceptions import (
    UsuarioDuplicadoException,
    UsuarioInactivoException,
    DatosUsuarioInvalidosException
)
from infrastructure.persistence.repositories.usuario_repository import UsuarioRepository
from infrastructure.persistence.repositories.rol_repository import RolRepository
from infrastructure.services.password_service import PasswordService
from infrastructure.services.token_service import TokenService
from infrastructure.services.email_service import EmailService


@method_decorator(csrf_protect, name='dispatch')
class LoginView(View):
    """
    Vista para el login de usuarios.
    
    Inyecta el caso de uso LoginUsuario y maneja la autenticación.
    """
    
    def __init__(self):
        """Inyección de dependencias."""
        self.login_usuario = LoginUsuario(
            usuario_repo=UsuarioRepository(),
            rol_repo=RolRepository(),
            password_service=PasswordService()
        )
    
    def get(self, request: HttpRequest) -> HttpResponse:
        """
        Muestra el formulario de login.
        
        Args:
            request: Objeto HttpRequest de Django
            
        Returns:
            HttpResponse con el template de login
        """
        # Si ya está autenticado, redirigir al dashboard
        if request.session.get('usuario_id'):
            return redirect('dashboard')
        
        return render(request, 'auth/login.html')
    
    def post(self, request: HttpRequest) -> HttpResponse:
        """
        Procesa el login del usuario.
        
        Args:
            request: Objeto HttpRequest con datos POST
            
        Returns:
            JsonResponse si es AJAX, HttpResponse normal si no
        """
        identificador = request.POST.get('identificador', '').strip()
        password = request.POST.get('password', '')
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        # Validar campos requeridos
        if not identificador or not password:
            error_msg = 'Todos los campos son obligatorios'
            if is_ajax:
                return JsonResponse({'success': False, 'message': error_msg}, status=400)
            messages.error(request, error_msg)
            return render(request, 'auth/login.html', {'identificador': identificador})
        
        try:
            # Crear DTO para el caso de uso
            login_dto = LoginDTO(identificador=identificador, password=password)
            
            # Ejecutar caso de uso
            resultado = self.login_usuario.execute(login_dto)
            
            # Guardar datos en sesión
            request.session['usuario_id'] = resultado.usuario.id
            request.session['usuario_nombre'] = resultado.usuario.nombre_completo
            request.session['usuario_email'] = resultado.usuario.email
            request.session['rol_id'] = resultado.usuario.rol_id
            request.session['rol_nombre'] = resultado.usuario.rol_nombre
            
            success_msg = f'¡Bienvenido {resultado.usuario.nombre_completo}!'
            if is_ajax:
                return JsonResponse({
                    'success': True,
                    'message': success_msg,
                    'redirect': '/'
                })
            
            messages.success(request, success_msg)
            return redirect('dashboard')
            
        except CredencialesInvalidasException:
            error_msg = 'Credenciales inválidas. Verifica tu usuario y contraseña.'
        except UsuarioInactivoException:
            error_msg = 'Tu cuenta está inactiva. Contacta al administrador.'
        except IntentosLoginExcedidosException as e:
            error_msg = str(e)
        except Exception as e:
            error_msg = f'Error al iniciar sesión: {str(e)}'
        
        if is_ajax:
            return JsonResponse({'success': False, 'message': error_msg}, status=400)
        
        messages.error(request, error_msg)
        return render(request, 'auth/login.html', {'identificador': identificador})


class LogoutView(View):
    """
    Vista para cerrar sesión del usuario.
    """
    
    def get(self, request: HttpRequest) -> HttpResponse:
        """
        Cierra la sesión del usuario.
        
        Args:
            request: Objeto HttpRequest
            
        Returns:
            HttpResponse con redirección al login
        """
        request.session.flush()
        messages.success(request, 'Has cerrado sesión correctamente')
        return redirect('auth:login')


@method_decorator(csrf_protect, name='dispatch')
class RegistroView(View):
    """
    Vista para registro de nuevos usuarios.
    """
    
    def __init__(self):
        """Inyección de dependencias."""
        self.registrar_usuario = RegistrarUsuario(
            usuario_repo=UsuarioRepository(),
            rol_repo=RolRepository(),
            password_service=PasswordService()
        )
    
    def get(self, request: HttpRequest) -> HttpResponse:
        """
        Muestra el formulario de registro.
        
        Args:
            request: Objeto HttpRequest
            
        Returns:
            HttpResponse con template de registro
        """
        # Si ya está autenticado, redirigir
        if request.session.get('usuario_id'):
            return redirect('dashboard')
        
        return render(request, 'auth/registro.html')
    
    def post(self, request: HttpRequest) -> HttpResponse:
        """
        Procesa el registro de un nuevo usuario.
        
        Args:
            request: Objeto HttpRequest con datos POST
            
        Returns:
            HttpResponse con redirección o errores
        """
        # Obtener datos del formulario
        nombre_completo = request.POST.get('nombre_completo', '').strip()
        email = request.POST.get('email', '').strip()
        username = request.POST.get('username', '').strip()
        telefono = request.POST.get('telefono', '').strip()
        password = request.POST.get('password', '')
        password_confirmacion = request.POST.get('password_confirmacion', '')
        
        # Validar campos requeridos
        if not all([nombre_completo, email, username, password, password_confirmacion]):
            messages.error(request, 'Todos los campos son obligatorios')
            return self._render_form(request, locals())
        
        # Validar que las contraseñas coincidan
        if password != password_confirmacion:
            messages.error(request, 'Las contraseñas no coinciden')
            return self._render_form(request, locals())
        
        try:
            # Crear DTO para el caso de uso
            # Por defecto, los nuevos registros tienen rol de Cajero (ajustar según lógica de negocio)
            rol_repository = RolRepository()
            rol_cajero = rol_repository.obtener_por_nombre('Cajero')
            
            dto = CrearUsuarioDTO(
                nombre_completo=nombre_completo,
                email=email,
                username=username,
                telefono=telefono if telefono else None,
                password=password,
                rol_id=rol_cajero.id if rol_cajero else 3  # Rol Cajero por defecto
            )
            
            # Ejecutar caso de uso
            usuario = self.registrar_usuario.execute(dto)
            
            messages.success(request, '¡Registro exitoso! Ya puedes iniciar sesión.')
            return redirect('auth:login')
            
        except UsuarioDuplicadoException as e:
            messages.error(request, str(e))
        except DatosUsuarioInvalidosException as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f'Error al registrar usuario: {str(e)}')
        
        return self._render_form(request, locals())
    
    def _render_form(self, request: HttpRequest, data: dict) -> HttpResponse:
        """
        Renderiza el formulario con los datos previos.
        
        Args:
            request: Objeto HttpRequest
            data: Diccionario con datos del formulario
            
        Returns:
            HttpResponse con template
        """
        return render(request, 'auth/registro.html', {
            'nombre_completo': data.get('nombre_completo', ''),
            'email': data.get('email', ''),
            'username': data.get('username', ''),
            'telefono': data.get('telefono', ''),
        })


@method_decorator(csrf_protect, name='dispatch')
class RecuperarPasswordView(View):
    """
    Vista para solicitar recuperación de contraseña.
    """
    
    def __init__(self):
        """Inyección de dependencias."""
        self.usuario_repo = UsuarioRepository()
        self.token_service = TokenService()
        self.email_service = EmailService()
    
    def get(self, request: HttpRequest) -> HttpResponse:
        """
        Muestra el formulario de recuperación.
        
        Args:
            request: Objeto HttpRequest
            
        Returns:
            HttpResponse con template
        """
        return render(request, 'auth/recuperar_password.html')
    
    def post(self, request: HttpRequest) -> HttpResponse:
        """
        Procesa la solicitud de recuperación.
        
        Args:
            request: Objeto HttpRequest con datos POST
            
        Returns:
            HttpResponse con redirección o errores
        """
        email = request.POST.get('email', '').strip()
        
        if not email:
            messages.error(request, 'El email es obligatorio')
            return render(request, 'auth/recuperar_password.html')
        
        try:
            # Buscar usuario por email
            usuario = self.usuario_repo.obtener_por_email(email)
            
            if usuario:
                # Generar token de recuperación
                token = self.token_service.generar_token()
                fecha_expiracion = self.token_service.calcular_expiracion()
                
                # Guardar token en base de datos
                from infrastructure.persistence.models import TokenRecuperacion
                TokenRecuperacion.objects.create(
                    usuario_id=usuario.id,
                    token=token,
                    fecha_expiracion=fecha_expiracion
                )
                
                # Enviar email con el token
                self.email_service.enviar_recuperacion_password(
                    usuario.email,
                    usuario.nombre_completo,
                    token
                )
            
            # Siempre mostrar el mismo mensaje (seguridad)
            messages.success(
                request,
                'Si el email existe, recibirás instrucciones para recuperar tu contraseña.'
            )
            return redirect('auth:login')
            
        except Exception as e:
            messages.error(request, 'Error al procesar la solicitud. Intenta nuevamente.')
        
        return render(request, 'auth/recuperar_password.html', {'email': email})


@method_decorator(csrf_protect, name='dispatch')
class RestablecerPasswordView(View):
    """
    Vista para restablecer contraseña con token.
    """
    
    def __init__(self):
        """Inyección de dependencias."""
        self.usuario_repo = UsuarioRepository()
        self.password_service = PasswordService()
        self.token_service = TokenService()
    
    def get(self, request: HttpRequest, token: str) -> HttpResponse:
        """
        Muestra el formulario de restablecimiento.
        
        Args:
            request: Objeto HttpRequest
            token: Token de recuperación
            
        Returns:
            HttpResponse con template
        """
        # Validar token
        if not self._validar_token(token):
            messages.error(request, 'El enlace de recuperación es inválido o ha expirado.')
            return redirect('auth:login')
        
        return render(request, 'auth/restablecer_password.html', {'token': token})
    
    def post(self, request: HttpRequest, token: str) -> HttpResponse:
        """
        Procesa el restablecimiento de contraseña.
        
        Args:
            request: Objeto HttpRequest con datos POST
            token: Token de recuperación
            
        Returns:
            HttpResponse con redirección o errores
        """
        password = request.POST.get('password', '')
        password_confirmacion = request.POST.get('password_confirmacion', '')
        
        # Validar campos
        if not password or not password_confirmacion:
            messages.error(request, 'Todos los campos son obligatorios')
            return render(request, 'auth/restablecer_password.html', {'token': token})
        
        if password != password_confirmacion:
            messages.error(request, 'Las contraseñas no coinciden')
            return render(request, 'auth/restablecer_password.html', {'token': token})
        
        try:
            # Validar token y obtener usuario
            from infrastructure.persistence.models import TokenRecuperacion
            token_obj = TokenRecuperacion.objects.filter(
                token=token,
                usado=False
            ).first()
            
            if not token_obj or not token_obj.esta_vigente():
                raise TokenExpiradoException('El token ha expirado')
            
            # Validar fortaleza de la nueva contraseña
            es_valida, errores = self.password_service.validar_fortaleza(password)
            if not es_valida:
                for error in errores:
                    messages.error(request, error)
                return render(request, 'auth/restablecer_password.html', {'token': token})
            
            # Actualizar contraseña
            usuario = self.usuario_repo.obtener_por_id(token_obj.usuario_id)
            if usuario:
                # Encriptar nueva contraseña
                password_hash = self.password_service.encriptar(password)
                
                # Actualizar en base de datos
                from infrastructure.persistence.models import Usuario as UsuarioModel
                UsuarioModel.objects.filter(id=usuario.id).update(
                    password_hash=password_hash
                )
                
                # Marcar token como usado
                token_obj.usado = True
                token_obj.save()
                
                messages.success(request, 'Contraseña actualizada exitosamente. Ya puedes iniciar sesión.')
                return redirect('auth:login')
            
        except TokenExpiradoException:
            messages.error(request, 'El enlace de recuperación ha expirado.')
        except PasswordInvalidaException as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f'Error al restablecer contraseña: {str(e)}')
        
        return render(request, 'auth/restablecer_password.html', {'token': token})
    
    def _validar_token(self, token: str) -> bool:
        """
        Valida si un token es válido y no ha expirado.
        
        Args:
            token: Token a validar
            
        Returns:
            True si el token es válido
        """
        from infrastructure.persistence.models import TokenRecuperacion
        token_obj = TokenRecuperacion.objects.filter(
            token=token,
            usado=False
        ).first()
        
        return token_obj is not None and token_obj.esta_vigente()
