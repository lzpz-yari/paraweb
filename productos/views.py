from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.db import transaction
from django.db.models import Sum, Count
from django.db.models.functions import TruncDate, TruncWeek, TruncMonth, TruncYear
from django.utils import timezone
from .models import Producto, Venta, DetalleVenta 
from django.contrib.auth.forms import AuthenticationForm
from .forms import BusquedaProductoForm
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
    """Punto de venta optimizado"""
    form = BusquedaProductoForm(request.GET or None)
    
    
    productos = Producto.objects.filter(activo=True).only(
        'id', 'nombre', 'codigo_barras', 'precio_venta', 
        'stock', 'imagen', 'imagen_thumbnail'
    )
    
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
    
    
    productos = productos.order_by('-activo', 'nombre')[:50]  
    
    return render(request, 'productos/punto_venta.html', {
        'productos': productos,
        'form': form
    })

@login_required
@require_POST
def procesar_venta(request):
    """Procesar venta con IVA incluido"""
    try:
        datos = json.loads(request.body)
        items = datos.get('items', [])
        
        if not items or len(items) == 0:
            return JsonResponse({
                'error': 'El carrito está vacío'
            }, status=400)
        
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
        
        with transaction.atomic():
            venta = Venta.objects.create(estado='completada')
            
            for item in items:
                try:
                    producto = Producto.objects.get(id=item['producto_id'])
                except Producto.DoesNotExist:
                    raise ValueError(f'Producto ID {item["producto_id"]} no encontrado')
                
                cantidad = int(item['cantidad'])
                precio_unitario = Decimal(str(item['precio_unitario']))
                
                if producto.stock < cantidad:
                    raise ValueError(
                        f'Stock insuficiente para {producto.nombre}. '
                        f'Disponible: {producto.stock}, Solicitado: {cantidad}'
                    )
                
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
            'subtotal': str(venta.subtotal),
            'iva': str(venta.iva),
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
    """Ver ticket"""
    venta = get_object_or_404(Venta, id=venta_id)
    contexto = {
        'venta': venta,
    }
    return render(request, 'productos/ticket_venta.html', contexto)


@login_required
def ventas_del_dia(request):
    """Vista para que el cajero vea el total de ventas del día"""
    from datetime import timedelta
    
    ahora = timezone.now()
    hace_24h = ahora - timedelta(hours=24)
    
    ventas_hoy = Venta.objects.filter(
        fecha__gte=hace_24h,
        estado='completada'
    )
    
    total_ventas = ventas_hoy.aggregate(
        total=Sum('total'),
        cantidad=Count('id')
    )
    
    ventas_list = ventas_hoy.select_related().prefetch_related('detalles__producto')
    
    contexto = {
        'fecha': ahora.date(),
        'total_dinero': total_ventas['total'] or 0,
        'cantidad_ventas': total_ventas['cantidad'] or 0,
        'ventas': ventas_list
    }
    
    return render(request, 'productos/ventas_del_dia.html', contexto)


@login_required
def reportes_ventas(request):
    """Vista de reportes para administradores"""
    if not request.user.is_staff:
        return redirect('productos:punto_venta')
    
    tipo_reporte = request.GET.get('tipo', 'diario')
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    
    ventas = Venta.objects.filter(estado='completada')
    
    if fecha_inicio:
        ventas = ventas.filter(fecha__gte=fecha_inicio)
    if fecha_fin:
        ventas = ventas.filter(fecha__lte=fecha_fin)
    
    if tipo_reporte == 'diario':
        ventas_agrupadas = ventas.annotate(
            periodo=TruncDate('fecha')
        ).values('periodo').annotate(
            total=Sum('total'),
            cantidad=Count('id')
        ).order_by('-periodo')
        
    elif tipo_reporte == 'semanal':
        ventas_agrupadas = ventas.annotate(
            periodo=TruncWeek('fecha')
        ).values('periodo').annotate(
            total=Sum('total'),
            cantidad=Count('id')
        ).order_by('-periodo')
        
    elif tipo_reporte == 'mensual':
        ventas_agrupadas = ventas.annotate(
            periodo=TruncMonth('fecha')
        ).values('periodo').annotate(
            total=Sum('total'),
            cantidad=Count('id')
        ).order_by('-periodo')
        
    elif tipo_reporte == 'anual':
        ventas_agrupadas = ventas.annotate(
            periodo=TruncYear('fecha')
        ).values('periodo').annotate(
            total=Sum('total'),
            cantidad=Count('id')
        ).order_by('-periodo')
    
    totales_generales = ventas.aggregate(
        total_dinero=Sum('total'),
        total_ventas=Count('id')
    )
    
    productos_top = DetalleVenta.objects.filter(
        venta__in=ventas
    ).values(
        'producto__nombre'
    ).annotate(
        cantidad_vendida=Sum('cantidad'),
        ingresos=Sum('subtotal')
    ).order_by('-cantidad_vendida')[:10]
    
    contexto = {
        'tipo_reporte': tipo_reporte,
        'ventas_agrupadas': ventas_agrupadas,
        'totales_generales': totales_generales,
        'productos_top': productos_top,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
    }
    
    return render(request, 'productos/reportes_ventas.html', contexto)


def login_view(request):
    """Vista de login"""
    if request.user.is_authenticated:
        return redirect('productos:punto_venta')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                auth_login(request, user)
                return redirect('productos:punto_venta')
    else:
        form = AuthenticationForm()
    
    return render(request, 'productos/login.html', {'form': form})

@login_required
def logout_view(request):
    """Vista de logout"""
    auth_logout(request)
    return redirect('productos:login')