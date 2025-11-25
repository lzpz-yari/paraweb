"""
URLs de la aplicación web (interfaces).

Configuración de rutas para autenticación, usuarios y perfil.
"""

from django.urls import path, include
from interfaces.web.views import auth_views, usuario_views, perfil_views, dashboard_views

# URLs de autenticación
auth_patterns = [
    path('login', auth_views.LoginView.as_view(), name='login'),
    path('logout', auth_views.LogoutView.as_view(), name='logout'),
    path('registro', auth_views.RegistroView.as_view(), name='registro'),
    path('recuperar-password', auth_views.RecuperarPasswordView.as_view(), name='recuperar-password'),
    path('restablecer-password/<str:token>', auth_views.RestablecerPasswordView.as_view(), name='restablecer-password'),
]

# URLs de usuarios
usuarios_patterns = [
    path('', usuario_views.UsuarioListView.as_view(), name='lista'),
    path('crear', usuario_views.UsuarioCreateView.as_view(), name='crear'),
    path('<int:usuario_id>/editar', usuario_views.UsuarioUpdateView.as_view(), name='editar'),
    path('<int:usuario_id>/eliminar', usuario_views.UsuarioDeleteView.as_view(), name='eliminar'),
]

# URLs de perfil
perfil_patterns = [
    path('', perfil_views.PerfilView.as_view(), name='detalle'),
    path('cambiar-password', perfil_views.CambiarPasswordView.as_view(), name='cambiar-password'),
]

# URLs principales
urlpatterns = [
    path('', dashboard_views.DashboardView.as_view(), name='dashboard'),
    path('auth/', include((auth_patterns, 'auth'))),
    path('usuarios/', include((usuarios_patterns, 'usuarios'))),
    path('perfil/', include((perfil_patterns, 'perfil'))),
]
