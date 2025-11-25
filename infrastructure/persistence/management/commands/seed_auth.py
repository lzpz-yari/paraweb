"""
Management command para poblar datos iniciales.

Comando Django para crear roles y permisos.
Uso: python manage.py seed_auth
"""
from django.core.management.base import BaseCommand
from infrastructure.persistence.models import Rol, Permiso


class Command(BaseCommand):
    """Comando para poblar datos de autenticación."""
    
    help = 'Crea roles y permisos iniciales del sistema'
    
    def handle(self, *args, **options):
        """Ejecuta el comando."""
        self.stdout.write("=" * 60)
        self.stdout.write(self.style.SUCCESS("SEED DE DATOS INICIALES - AUTENTICACIÓN"))
        self.stdout.write("=" * 60)
        
        # Crear permisos
        self.stdout.write("\n1. Creando permisos...")
        permisos = self.crear_permisos()
        
        # Crear roles
        self.stdout.write("\n2. Creando roles...")
        self.crear_roles(permisos)
        
        # Resumen
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.SUCCESS("✓ SEED COMPLETADO EXITOSAMENTE"))
        self.stdout.write("=" * 60)
        self.stdout.write("\nRoles creados:")
        for rol in Rol.objects.all():
            self.stdout.write(f"  - {rol.nombre}: {rol.permisos.count()} permisos")
        
        self.stdout.write(f"\nTotal de permisos: {Permiso.objects.count()}")
        self.stdout.write(f"Total de roles: {Rol.objects.count()}")
    
    def crear_permisos(self):
        """Crea los permisos del sistema."""
        
        permisos_data = [
            # Módulo Ventas
            {'codigo': 'ventas.ver', 'nombre': 'Ver Ventas', 'modulo': 'ventas', 
             'descripcion': 'Visualizar ventas y órdenes'},
            {'codigo': 'ventas.crear', 'nombre': 'Crear Ventas', 'modulo': 'ventas',
             'descripcion': 'Crear nuevas ventas y órdenes'},
            {'codigo': 'ventas.editar', 'nombre': 'Editar Ventas', 'modulo': 'ventas',
             'descripcion': 'Modificar ventas existentes'},
            {'codigo': 'ventas.eliminar', 'nombre': 'Eliminar Ventas', 'modulo': 'ventas',
             'descripcion': 'Eliminar ventas'},
            
            # Módulo Inventario
            {'codigo': 'inventario.ver', 'nombre': 'Ver Inventario', 'modulo': 'inventario',
             'descripcion': 'Visualizar inventario y productos'},
            {'codigo': 'inventario.crear', 'nombre': 'Crear Productos', 'modulo': 'inventario',
             'descripcion': 'Crear nuevos productos'},
            {'codigo': 'inventario.editar', 'nombre': 'Editar Inventario', 'modulo': 'inventario',
             'descripcion': 'Modificar productos e inventario'},
            {'codigo': 'inventario.eliminar', 'nombre': 'Eliminar Productos', 'modulo': 'inventario',
             'descripcion': 'Eliminar productos'},
            
            # Módulo Cocina
            {'codigo': 'cocina.ver', 'nombre': 'Ver Órdenes Cocina', 'modulo': 'cocina',
             'descripcion': 'Visualizar órdenes de cocina'},
            {'codigo': 'cocina.gestionar', 'nombre': 'Gestionar Cocina', 'modulo': 'cocina',
             'descripcion': 'Cambiar estado de órdenes de cocina'},
            
            # Módulo Reportes
            {'codigo': 'reportes.ver', 'nombre': 'Ver Reportes', 'modulo': 'reportes',
             'descripcion': 'Visualizar reportes y estadísticas'},
            {'codigo': 'reportes.exportar', 'nombre': 'Exportar Reportes', 'modulo': 'reportes',
             'descripcion': 'Exportar reportes a PDF/Excel'},
            
            # Módulo Configuración
            {'codigo': 'configuracion.ver', 'nombre': 'Ver Configuración', 'modulo': 'configuracion',
             'descripcion': 'Ver configuración del sistema'},
            {'codigo': 'configuracion.editar', 'nombre': 'Editar Configuración', 'modulo': 'configuracion',
             'descripcion': 'Modificar configuración del sistema'},
            
            # Módulo Usuarios
            {'codigo': 'usuarios.ver', 'nombre': 'Ver Usuarios', 'modulo': 'usuarios',
             'descripcion': 'Visualizar usuarios del sistema'},
            {'codigo': 'usuarios.crear', 'nombre': 'Crear Usuarios', 'modulo': 'usuarios',
             'descripcion': 'Crear nuevos usuarios'},
            {'codigo': 'usuarios.editar', 'nombre': 'Editar Usuarios', 'modulo': 'usuarios',
             'descripcion': 'Modificar usuarios existentes'},
            {'codigo': 'usuarios.eliminar', 'nombre': 'Eliminar Usuarios', 'modulo': 'usuarios',
             'descripcion': 'Eliminar usuarios'},
        ]
        
        permisos_creados = []
        
        for permiso_data in permisos_data:
            permiso, created = Permiso.objects.get_or_create(
                codigo=permiso_data['codigo'],
                defaults={
                    'nombre': permiso_data['nombre'],
                    'modulo': permiso_data['modulo'],
                    'descripcion': permiso_data['descripcion']
                }
            )
            permisos_creados.append(permiso)
            
            if created:
                self.stdout.write(self.style.SUCCESS(f"✓ Permiso creado: {permiso.codigo}"))
            else:
                self.stdout.write(f"- Permiso ya existe: {permiso.codigo}")
        
        return permisos_creados
    
    def crear_roles(self, permisos):
        """Crea los roles predefinidos del sistema."""
        
        permisos_dict = {p.codigo: p for p in permisos}
        
        roles_data = [
            {
                'nombre': 'Administrador',
                'descripcion': 'Acceso total al sistema',
                'is_sistema': True,
                'permisos': list(permisos_dict.keys())
            },
            {
                'nombre': 'Gerente',
                'descripcion': 'Gestión operativa del restaurante',
                'is_sistema': True,
                'permisos': [
                    'ventas.ver', 'ventas.crear', 'ventas.editar',
                    'inventario.ver', 'inventario.crear', 'inventario.editar',
                    'cocina.ver', 'cocina.gestionar',
                    'reportes.ver', 'reportes.exportar',
                    'configuracion.ver',
                    'usuarios.ver'
                ]
            },
            {
                'nombre': 'Cajero',
                'descripcion': 'Ventas y cobros',
                'is_sistema': True,
                'permisos': [
                    'ventas.ver', 'ventas.crear',
                    'inventario.ver',
                    'reportes.ver'
                ]
            },
            {
                'nombre': 'Mesero',
                'descripcion': 'Toma de órdenes',
                'is_sistema': True,
                'permisos': [
                    'ventas.ver', 'ventas.crear',
                    'cocina.ver'
                ]
            },
            {
                'nombre': 'Cocinero',
                'descripcion': 'Gestión de cocina',
                'is_sistema': True,
                'permisos': [
                    'cocina.ver', 'cocina.gestionar'
                ]
            },
            {
                'nombre': 'Bartender',
                'descripcion': 'Gestión de bar',
                'is_sistema': True,
                'permisos': [
                    'cocina.ver', 'cocina.gestionar'
                ]
            }
        ]
        
        for rol_data in roles_data:
            rol, created = Rol.objects.get_or_create(
                nombre=rol_data['nombre'],
                defaults={
                    'descripcion': rol_data['descripcion'],
                    'is_sistema': rol_data['is_sistema'],
                    'is_active': True
                }
            )
            
            # Asignar permisos
            permisos_rol = [permisos_dict[codigo] for codigo in rol_data['permisos'] 
                            if codigo in permisos_dict]
            rol.permisos.set(permisos_rol)
            
            if created:
                self.stdout.write(self.style.SUCCESS(
                    f"✓ Rol creado: {rol.nombre} con {len(permisos_rol)} permisos"
                ))
            else:
                self.stdout.write(f"- Rol ya existe: {rol.nombre}")
