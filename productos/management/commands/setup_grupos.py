from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission


class Command(BaseCommand):
    help = 'Configura grupos y permisos'

    def handle(self, *args, **kwargs):
        self.stdout.write('Configurando grupos y permisos...')
        
        cajero_group, created = Group.objects.get_or_create(name='Cajero')
        if created:
            self.stdout.write(self.style.SUCCESS('Grupo Cajero creado'))
        else:
            self.stdout.write('Grupo Cajero ya existe')
        
        admin_group, created = Group.objects.get_or_create(name='Administrador')
        if created:
            self.stdout.write(self.style.SUCCESS('Grupo Administrador creado'))
        else:
            self.stdout.write('Grupo Administrador ya existe')
        
        cajero_group.permissions.clear()
        admin_group.permissions.clear()
        
        cajero_permissions = [
            'view_producto',
            'add_venta',
            'view_venta',
            'add_detalleventa',
            'view_detalleventa',
        ]
        
        for codename in cajero_permissions:
            try:
                perm = Permission.objects.get(codename=codename)
                cajero_group.permissions.add(perm)
            except Permission.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'Permiso {codename} no encontrado'))
        
        self.stdout.write(self.style.SUCCESS(f'Cajero: {cajero_group.permissions.count()} permisos'))
        
        admin_permissions = Permission.objects.all()
        for perm in admin_permissions:
            admin_group.permissions.add(perm)
        
        self.stdout.write(self.style.SUCCESS(f'Administrador: {admin_group.permissions.count()} permisos'))
        self.stdout.write(self.style.SUCCESS('Grupos configurados exitosamente'))