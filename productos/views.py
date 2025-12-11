from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.db import transaction
from .models import Producto, Venta, DetalleVenta
from django.db.models import Q
import json


def lista_productos(request):
    """Lista pública de productos"""
    productos = Producto.objects.all()
    contexto = {
        'productos': productos,
    }
    return render(request, 'productos/lista_productos.html', contexto)


def detalle_producto(request, producto_id):
    """Detalle público de producto"""
    producto = get_object_or_404(Producto, id=producto_id)
    contexto = {
        'producto': producto,
    }
    return render(request, 'productos/detalle_producto.html', contexto)


@login_required
def punto_venta(request):
    """Punto de venta - requiere login"""
    productos = Producto.objects.all()
    
    buscar = request.GET.get('buscar', '').strip()
    if buscar:
        productos = productos.filter(
            Q(nombre__icontains=buscar) | 
            Q(codigo_barras__icontains=buscar)
        )
    
    activo = request.GET.get('activo', '')
    if activo == '1':
        productos = productos.filter(activo=True)
    elif activo == '0':
        productos = productos.filter(activo=False)
    
    productos = productos.order_by('-activo', 'nombre')
    
    contexto = {
        'productos': productos,
    }
    
    return render(request, 'productos/punto_venta.html', contexto)


@login_required
@require_POST
def procesar_venta(request):
    """Procesar venta - requiere login"""
    try:
        datos = json.loads(request.body)
        items = datos.get('items', [])
        
        if not items:
            return JsonResponse({
                'error': 'Carrito vacío'
            }, status=400)
        
        with transaction.atomic():
            venta = Venta.objects.create(estado='completada')
            
            for item in items:
                producto_id = item.get('producto_id')
                cantidad = item.get('cantidad')
                precio_unitario = item.get('precio_unitario')
                
                if not all([producto_id, cantidad, precio_unitario]):
                    raise ValueError('Datos incompletos')
                
                try:
                    producto = Producto.objects.get(id=producto_id, activo=True)
                except Producto.DoesNotExist:
                    raise ValueError(f'Producto {producto_id} no encontrado')
                
                if producto.stock < cantidad:
                    raise ValueError(f'Stock insuficiente: {producto.nombre}')
                
                DetalleVenta.objects.create(
                    venta=venta,
                    producto=producto,
                    cantidad=cantidad,
                    precio_unitario=precio_unitario
                )
                
                producto.stock -= cantidad
                producto.save()
            
            venta.calcular_total()
        
        return JsonResponse({
            'venta_id': venta.id,
            'total': str(venta.total),
            'cantidad_items': venta.cantidad_items(),
            'fecha': venta.fecha.strftime('%d/%m/%Y %H:%M')
        })
    
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)
    
    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSON inválido'}, status=400)
    
    except Exception as e:
        return JsonResponse({'error': f'Error: {str(e)}'}, status=500)


@login_required
def ticket_venta(request, venta_id):
    """Ver ticket - requiere login"""
    venta = get_object_or_404(Venta, id=venta_id)
    contexto = {
        'venta': venta,
    }
    return render(request, 'productos/ticket_venta.html', contexto)


def login_view(request):
    """Vista de login"""
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('/admin/')
        return redirect('productos:punto_venta')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            auth_login(request, user)
            
            if user.is_staff:
                return redirect('/admin/')
            else:
                return redirect('productos:punto_venta')
        else:
            return render(request, 'productos/login.html', {
                'error': 'Usuario o contraseña incorrectos'
            })
    
    return render(request, 'productos/login.html')


@login_required
def logout_view(request):
    """Vista de logout"""
    auth_logout(request)
    return redirect('productos:login')