"""
Caso de Uso: Listar Usuarios - Capa de Aplicación.

Implementa la lógica para listar usuarios con filtros y paginación.
"""
from typing import List, Dict
from application.dtos.usuario_dto import ListarUsuariosDTO, UsuarioDTO
from application.interfaces.repositories import IUsuarioRepository, IRolRepository


class ListarUsuarios:
    """
    Caso de uso para listar usuarios con filtros.
    
    Responsabilidad única: Obtener lista paginada de usuarios.
    """
    
    def __init__(
        self,
        usuario_repo: IUsuarioRepository,
        rol_repo: IRolRepository
    ):
        """
        Constructor con inyección de dependencias.
        
        Args:
            usuario_repo: Repositorio de usuarios
            rol_repo: Repositorio de roles
        """
        self.usuario_repo = usuario_repo
        self.rol_repo = rol_repo
    
    def execute(self, dto: ListarUsuariosDTO) -> Dict:
        """
        Ejecuta la búsqueda de usuarios.
        
        Args:
            dto: DTO con filtros y paginación
            
        Returns:
            Dict con usuarios y metadata de paginación
        """
        # Calcular offset
        offset = (dto.pagina - 1) * dto.por_pagina
        
        # Obtener usuarios
        usuarios = self.usuario_repo.listar(
            busqueda=dto.busqueda,
            rol_id=dto.rol_id,
            is_active=dto.is_active,
            limite=dto.por_pagina,
            offset=offset
        )
        
        # Contar total
        total = self.usuario_repo.contar(
            busqueda=dto.busqueda,
            rol_id=dto.rol_id,
            is_active=dto.is_active
        )
        
        # Convertir a DTOs
        usuarios_dtos = [
            self._convertir_a_dto(usuario)
            for usuario in usuarios
        ]
        
        # Calcular páginas
        total_paginas = (total + dto.por_pagina - 1) // dto.por_pagina
        
        return {
            'usuarios': usuarios_dtos,
            'pagina_actual': dto.pagina,
            'por_pagina': dto.por_pagina,
            'total': total,
            'total_paginas': total_paginas,
            'tiene_siguiente': dto.pagina < total_paginas,
            'tiene_anterior': dto.pagina > 1
        }
    
    def _convertir_a_dto(self, usuario) -> UsuarioDTO:
        """
        Convierte entidad Usuario a DTO.
        
        Args:
            usuario: Entidad Usuario
            
        Returns:
            DTO del usuario
        """
        # Obtener rol
        rol = self.rol_repo.obtener_por_id(usuario.rol_id)
        rol_nombre = rol.nombre if rol else "Sin Rol"
        
        return UsuarioDTO(
            id=usuario.id,
            email=usuario.email,
            username=usuario.username,
            nombre_completo=usuario.nombre_completo,
            telefono=usuario.telefono,
            rol_id=usuario.rol_id,
            rol_nombre=rol_nombre,
            is_active=usuario.is_active,
            fecha_registro=usuario.fecha_registro,
            ultimo_acceso=usuario.ultimo_acceso
        )
