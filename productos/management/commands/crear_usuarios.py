from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group


class Command(BaseCommand):
    help = 'Crea usuarios de prueba'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creando usuarios de prueba...')
        
        if User.objects.filter(username='cajero1').exists():
            self.stdout.write('Usuario cajero1 ya existe')
            cajero = User.objects.get(username='cajero1')
        else:
            cajero = User.objects.create_user(
                username='cajero1',
                password='cajero123',
                first_name='Maria',
                last_name='Garcia',
                email='cajero1@ejemplo.com'
            )
            self.stdout.write(self.style.SUCCESS('Usuario cajero1 creado'))
        
        cajero_group = Group.objects.get(name='Cajero')
        cajero.groups.clear()
        cajero.groups.add(cajero_group)
        
        if User.objects.filter(username='admin1').exists():
            self.stdout.write('Usuario admin1 ya existe')
            admin = User.objects.get(username='admin1')
        else:
            admin = User.objects.create_user(
                username='admin1',
                password='admin123',
                first_name='Juan',
                last_name='Perez',
                email='admin1@ejemplo.com',
                is_staff=True,
                is_superuser=True
            )
            self.stdout.write(self.style.SUCCESS('Usuario admin1 creado'))
        
        admin_group = Group.objects.get(name='Administrador')
        admin.groups.clear()
        admin.groups.add(admin_group)
        
        self.stdout.write(self.style.SUCCESS('Usuarios creados exitosamente'))
        self.stdout.write('')
        self.stdout.write('Credenciales:')
        self.stdout.write('  Cajero: cajero1 / cajero123')
        self.stdout.write('  Admin: admin1 / admin123')