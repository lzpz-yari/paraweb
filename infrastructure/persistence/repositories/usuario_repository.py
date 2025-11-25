"""
Repositorio de Usuario - Capa de Infraestructura.

Implementación del repositorio de usuarios usando Django ORM.
"""
from typing import Optional, List
from infrastructure.persistence.models import Usuario as UsuarioModel, Rol as RolModel
from core.entities.usuario import Usuario
from core.exceptions.usuario_exceptions import (
    UsuarioNoEncontradoException,
    UsuarioDuplicadoException
)


class UsuarioRepository:
    """
    Implementación del repositorio de usuarios.
    
    Convierte entre modelos Django y entidades del dominio.
    Aplica patrón Repository para abstraer el acceso a datos.
    """
    
    def guardar(self, usuario: Usuario) -> Usuario:
        """
        Guarda un usuario nuevo.
        
        Args:
            usuario: Entidad Usuario a guardar
            
        Returns:
            Usuario guardado con ID asignado
            
        Raises:
            UsuarioDuplicadoException: Si email o username ya existe
        """
        # Verificar duplicados
        if UsuarioModel.objects.filter(email=usuario.email).exists():
            raise UsuarioDuplicadoException('email', usuario.email)
        
        if UsuarioModel.objects.filter(username=usuario.username).exists():
            raise UsuarioDuplicadoException('username', usuario.username)
        
        # Crear modelo Django
        usuario_model = UsuarioModel(
            email=usuario.email,
            username=usuario.username,
            nombre_completo=usuario.nombre_completo,
            password_hash=usuario.password_hash,
            telefono=usuario.telefono,
            rol_id=usuario.rol_id,
            is_active=usuario.is_active
        )
        
        usuario_model.save()
        
        # Convertir a entidad y retornar
        return self._model_to_entity(usuario_model)
    
    def actualizar(self, usuario: Usuario) -> Usuario:
        """
        Actualiza un usuario existente.
        
        Args:
            usuario: Entidad Usuario a actualizar
            
        Returns:
            Usuario actualizado
            
        Raises:
            UsuarioNoEncontradoException: Si el usuario no existe
        """
        try:
            usuario_model = UsuarioModel.objects.get(id=usuario.id)
        except UsuarioModel.DoesNotExist:
            raise UsuarioNoEncontradoException(str(usuario.id))
        
        # Actualizar campos
        usuario_model.nombre_completo = usuario.nombre_completo
        usuario_model.telefono = usuario.telefono
        usuario_model.password_hash = usuario.password_hash
        usuario_model.rol_id = usuario.rol_id
        usuario_model.is_active = usuario.is_active
        usuario_model.ultimo_acceso = usuario.ultimo_acceso
        
        usuario_model.save()
        
        return self._model_to_entity(usuario_model)
    
    def obtener_por_id(self, usuario_id: int) -> Optional[Usuario]:
        """
        Obtiene un usuario por su ID.
        
        Args:
            usuario_id: ID del usuario
            
        Returns:
            Usuario si existe, None en caso contrario
        """
        try:
            usuario_model = UsuarioModel.objects.get(id=usuario_id)
            return self._model_to_entity(usuario_model)
        except UsuarioModel.DoesNotExist:
            return None
    
    def obtener_por_email(self, email: str) -> Optional[Usuario]:
        """
        Obtiene un usuario por su email.
        
        Args:
            email: Email del usuario
            
        Returns:
            Usuario si existe, None en caso contrario
        """
        try:
            usuario_model = UsuarioModel.objects.get(email=email.lower())
            return self._model_to_entity(usuario_model)
        except UsuarioModel.DoesNotExist:
            return None
    
    def obtener_por_username(self, username: str) -> Optional[Usuario]:
        """
        Obtiene un usuario por su username.
        
        Args:
            username: Username del usuario
            
        Returns:
            Usuario si existe, None en caso contrario
        """
        try:
            usuario_model = UsuarioModel.objects.get(username=username.lower())
            return self._model_to_entity(usuario_model)
        except UsuarioModel.DoesNotExist:
            return None
    
    def existe_email(self, email: str, excluir_id: Optional[int] = None) -> bool:
        """
        Verifica si existe un email.
        
        Args:
            email: Email a verificar
            excluir_id: ID de usuario a excluir de la búsqueda
            
        Returns:
            True si existe, False en caso contrario
        """
        query = UsuarioModel.objects.filter(email=email.lower())
        
        if excluir_id:
            query = query.exclude(id=excluir_id)
        
        return query.exists()
    
    def existe_username(self, username: str, excluir_id: Optional[int] = None) -> bool:
        """
        Verifica si existe un username.
        
        Args:
            username: Username a verificar
            excluir_id: ID de usuario a excluir de la búsqueda
            
        Returns:
            True si existe, False en caso contrario
        """
        query = UsuarioModel.objects.filter(username=username.lower())
        
        if excluir_id:
            query = query.exclude(id=excluir_id)
        
        return query.exists()
    
    def listar(
        self,
        busqueda: Optional[str] = None,
        rol_id: Optional[int] = None,
        is_active: Optional[bool] = None,
        limite: int = 20,
        offset: int = 0
    ) -> List[Usuario]:
        """
        Lista usuarios con filtros.
        
        Args:
            busqueda: Texto de búsqueda en email, username, nombre
            rol_id: Filtrar por rol
            is_active: Filtrar por estado
            limite: Máximo de registros
            offset: Offset para paginación
            
        Returns:
            Lista de usuarios que coinciden con los filtros
        """
        query = UsuarioModel.objects.all()
        
        # Aplicar filtros
        if busqueda:
            from django.db.models import Q
            query = query.filter(
                Q(email__icontains=busqueda) |
                Q(username__icontains=busqueda) |
                Q(nombre_completo__icontains=busqueda)
            )
        
        if rol_id is not None:
            query = query.filter(rol_id=rol_id)
        
        if is_active is not None:
            query = query.filter(is_active=is_active)
        
        # Aplicar paginación
        usuarios_models = query[offset:offset + limite]
        
        # Convertir a entidades
        return [
            self._model_to_entity(usuario_model)
            for usuario_model in usuarios_models
        ]
    
    def contar(
        self,
        busqueda: Optional[str] = None,
        rol_id: Optional[int] = None,
        is_active: Optional[bool] = None
    ) -> int:
        """
        Cuenta usuarios con filtros.
        
        Args:
            busqueda: Texto de búsqueda en email, username, nombre
            rol_id: Filtrar por rol
            is_active: Filtrar por estado
            
        Returns:
            Número de usuarios que coinciden con los filtros
        """
        query = UsuarioModel.objects.all()
        
        if busqueda:
            from django.db.models import Q
            query = query.filter(
                Q(email__icontains=busqueda) |
                Q(username__icontains=busqueda) |
                Q(nombre_completo__icontains=busqueda)
            )
        
        if rol_id is not None:
            query = query.filter(rol_id=rol_id)
        
        if is_active is not None:
            query = query.filter(is_active=is_active)
        
        return query.count()
    
    def eliminar(self, usuario_id: int) -> None:
        """
        Elimina (soft delete) un usuario.
        
        Args:
            usuario_id: ID del usuario a eliminar
            
        Raises:
            UsuarioNoEncontradoException: Si el usuario no existe
        """
        try:
            usuario_model = UsuarioModel.objects.get(id=usuario_id)
            usuario_model.is_active = False
            usuario_model.save()
        except UsuarioModel.DoesNotExist:
            raise UsuarioNoEncontradoException(str(usuario_id))
    
    def _model_to_entity(self, usuario_model: UsuarioModel) -> Usuario:
        """
        Convierte un modelo Django a entidad del dominio.
        
        Args:
            usuario_model: Modelo Django
            
        Returns:
            Entidad Usuario
        """
        return Usuario(
            id=usuario_model.id,
            email=usuario_model.email,
            username=usuario_model.username,
            nombre_completo=usuario_model.nombre_completo,
            password_hash=usuario_model.password_hash,
            telefono=usuario_model.telefono,
            rol_id=usuario_model.rol_id,
            is_active=usuario_model.is_active,
            fecha_registro=usuario_model.fecha_registro,
            ultimo_acceso=usuario_model.ultimo_acceso
        )
