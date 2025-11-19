from django.urls import path
from . import views

app_name = 'productos'

urlpatterns = [
    path('', views.lista_productos, name='lista'),
    
    path('<int:producto_id>/', views.detalle_producto, name='detalle'),
    path('pos/', views.punto_venta, name='punto_venta'),
]