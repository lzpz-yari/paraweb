"""
Vistas de Dashboard - Capa de Presentación.

Vista temporal de dashboard hasta implementar módulos completos.
"""

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.views import View


class DashboardView(View):
    """
    Vista principal del dashboard.
    
    Muestra información general del sistema según el rol del usuario.
    """
    
    def get(self, request: HttpRequest) -> HttpResponse:
        """
        Muestra el dashboard principal.
        
        Args:
            request: Objeto HttpRequest
            
        Returns:
            HttpResponse con template de dashboard
        """
        # Verificar autenticación
        if not request.session.get('usuario_id'):
            return redirect('auth:login')
        
        # Obtener datos del usuario desde la sesión
        context = {
            'usuario_nombre': request.session.get('usuario_nombre', 'Usuario'),
            'usuario_rol': request.session.get('usuario_rol', 'Sin rol'),
        }
        
        return render(request, 'dashboard/index.html', context)
