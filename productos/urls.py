from django.urls import path
from . import views

app_name = 'productos'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    path('', views.lista_productos, name='lista'),
    path('<int:producto_id>/', views.detalle_producto, name='detalle'),
    path('pos/', views.punto_venta, name='punto_venta'),
    path('pos/procesar/', views.procesar_venta, name='procesar_venta'),
    path('venta/<int:venta_id>/ticket/', views.ticket_venta, name='ticket_venta'),
]