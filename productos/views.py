from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.db import transaction
from .models import Producto, Venta, DetalleVenta
from .forms import CustomLoginForm, BusquedaProductoForm
from django.db.models import Q
from decimal import Decimal
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
    """Punto de venta con validaciones"""
    form = BusquedaProductoForm(request.GET or None)
    
    productos = Producto.objects.filter(activo=True)
    
    if form.is_valid():
        buscar = form.cleaned_data.get('buscar')
        activo = form.cleaned_data.get('activo')
        
        if buscar:
            productos = productos.filter(
                Q(nombre__icontains=buscar) |
                Q(codigo_barras__icontains=buscar)
            )
        
        if activo == '1':
            productos = productos.filter(activo=True)
        elif activo == '0':
            productos = productos.filter(activo=False)
    
    productos = productos.order_by('-activo', 'nombre')
    
    return render(request, 'productos/punto_venta.html', {
        'productos': productos,
        'form': form
    })


@login_required
@require_POST
def procesar_venta(request):
    """Procesar venta con validaciones del servidor"""
    try:
        datos = json.loads(request.body)
        items = datos.get('items', [])
        
        # Validación: verificar que haya items
        if not items or len(items) == 0:
            return JsonResponse({
                'error': 'El carrito está vacío'
            }, status=400)
        
        # Validación: verificar estructura de cada item
        errores = []
        for idx, item in enumerate(items):
            if not item.get('producto_id'):
                errores.append(f'Item {idx + 1}: ID de producto faltante')
            if not item.get('cantidad') or item['cantidad'] <= 0:
                errores.append(f'Item {idx + 1}: Cantidad inválida')
            if not item.get('precio_unitario') or item['precio_unitario'] <= 0:
                errores.append(f'Item {idx + 1}: Precio inválido')
        
        if errores:
            return JsonResponse({
                'error': ', '.join(errores)
            }, status=400)
        
        # Procesar venta en transacción atómica
        with transaction.atomic():
            venta = Venta.objects.create(estado='completada')
            
            for item in items:
                try:
                    producto = Producto.objects.get(id=item['producto_id'])
                except Producto.DoesNotExist:
                    raise ValueError(f'Producto ID {item["producto_id"]} no encontrado')
                
                cantidad = int(item['cantidad'])
                precio_unitario = Decimal(str(item['precio_unitario']))
                
                # Validar stock disponible
                if producto.stock < cantidad:
                    raise ValueError(
                        f'Stock insuficiente para {producto.nombre}. '
                        f'Disponible: {producto.stock}, Solicitado: {cantidad}'
                    )
                
                # Crear detalle de venta
                DetalleVenta.objects.create(
                    venta=venta,
                    producto=producto,
                    cantidad=cantidad,
                    precio_unitario=precio_unitario
                )
                
                # Actualizar stock
                producto.stock -= cantidad
                producto.save()
            
            # Calcular total de la venta
            venta.calcular_total()
        
        # Respuesta exitosa
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
        return JsonResponse({'error': 'Error interno del servidor'}, status=500)


@login_required
def ticket_venta(request, venta_id):
    """Ver ticket - requiere login"""
    venta = get_object_or_404(Venta, id=venta_id)
    contexto = {
        'venta': venta,
    }
    return render(request, 'productos/ticket_venta.html', contexto)


def login_view(request):
    """Vista de login con validaciones"""
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('/admin/')
        return redirect('productos:punto_venta')
    
    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                auth_login(request, user)
                
                if user.is_staff:
                    return redirect('/admin/')
                return redirect('productos:punto_venta')
            else:
                form.add_error(None, 'Usuario o contraseña incorrectos')
        
        return render(request, 'productos/login.html', {'form': form})
    
    else:
        form = CustomLoginForm()
        return render(request, 'productos/login.html', {'form': form})


@login_required
def logout_view(request):
    """Vista de logout"""
    auth_logout(request)
    return redirect('productos:login')