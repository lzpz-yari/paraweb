from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from decimal import Decimal
from productos.models import Producto, Venta, DetalleVenta
import json

class ListaProductosViewTest(TestCase):
    """Tests para vista lista_productos"""
    
    def test_lista_productos_publica(self):
        """La lista de productos debe ser pública"""
        Producto.objects.create(
            codigo_barras='1234567890',
            nombre='Producto Test',
            precio_compra=Decimal('10.00'),
            precio_venta=Decimal('15.00'),
            stock=100
        )
        
        response = self.client.get(reverse('productos:lista_productos'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'productos/lista_productos.html')
    
    def test_lista_productos_muestra_todos(self):
        """Debe mostrar todos los productos"""
        Producto.objects.create(
            codigo_barras='1111111111',
            nombre='Producto 1',
            precio_compra=Decimal('5.00'),
            precio_venta=Decimal('10.00'),
            stock=50
        )
        
        Producto.objects.create(
            codigo_barras='2222222222',
            nombre='Producto 2',
            precio_compra=Decimal('8.00'),
            precio_venta=Decimal('12.00'),
            stock=30
        )
        
        response = self.client.get(reverse('productos:lista_productos'))
        self.assertContains(response, 'Producto 1')
        self.assertContains(response, 'Producto 2')


class DetalleProductoViewTest(TestCase):
    """Tests para vista detalle_producto"""
    
    def test_detalle_producto_publico(self):
        """El detalle de producto debe ser público"""
        producto = Producto.objects.create(
            codigo_barras='1234567890',
            nombre='Producto Test',
            descripcion='Descripción detallada',
            precio_compra=Decimal('10.00'),
            precio_venta=Decimal('15.00'),
            stock=100
        )
        
        response = self.client.get(reverse('productos:detalle_producto', args=[producto.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'productos/detalle_producto.html')
        self.assertContains(response, 'Producto Test')
        self.assertContains(response, 'Descripción detallada')
    
    def test_detalle_producto_404(self):
        """Producto inexistente debe retornar 404"""
        response = self.client.get(reverse('productos:detalle_producto', args=[999]))
        self.assertEqual(response.status_code, 404)