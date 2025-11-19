from django.shortcuts import render, get_object_or_404
from .models import Producto
from django.db.models import Q

def lista_productos(request):
    productos = Producto.objects.all()
    contexto = {
        'productos': productos,
    }
    return render(request, 'productos/lista_productos.html', contexto)

def detalle_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    contexto = {
        'producto': producto,
    }
    return render(request, 'productos/detalle_producto.html', contexto)

def punto_venta(request):
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
    
    # CORREGIDO: El ordenamiento y return deben estar fuera de los if
    productos = productos.order_by('-activo', 'nombre')
    
    contexto = {
        'productos': productos,
    }
    
    # CORREGIDO: También corregí el nombre del template
    return render(request, 'productos/punto_venta.html', contexto)
    