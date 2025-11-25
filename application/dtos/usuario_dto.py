"""
DTOs de Usuario - Capa de Aplicación.

Data Transfer Objects para transferir datos de usuarios entre capas.
"""
from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class UsuarioDTO:
    """
    DTO para transferir datos de usuario entre capas.
    
    Attributes:
        id: ID del usuario
        email: Email del usuario
        username: Username del usuario
        nombre_completo: Nombre completo
        telefono: Teléfono (opcional)
        rol_id: ID del rol asignado
        rol_nombre: Nombre del rol
        is_active: Si el usuario está activo
        fecha_registro: Fecha de registro
        ultimo_acceso: Último acceso (opcional)
    """
    id: int
    email: str
    username: str
    nombre_completo: str
    rol_id: int
    rol_nombre: str
    is_active: bool
    telefono: Optional[str] = None
    fecha_registro: Optional[datetime] = None
    ultimo_acceso: Optional[datetime] = None


@dataclass
class CrearUsuarioDTO:
    """
    DTO para crear un nuevo usuario.
    
    Attributes:
        email: Email del usuario
        username: Username del usuario
        nombre_completo: Nombre completo
        password: Contraseña en texto plano
        rol_id: ID del rol a asignar
        telefono: Teléfono (opcional)
    """
    email: str
    username: str
    nombre_completo: str
    password: str
    rol_id: int
    telefono: Optional[str] = None


@dataclass
class ActualizarUsuarioDTO:
    """
    DTO para actualizar un usuario existente.
    
    Attributes:
        usuario_id: ID del usuario a actualizar
        nombre_completo: Nuevo nombre completo (opcional)
        telefono: Nuevo teléfono (opcional)
        rol_id: Nuevo rol (opcional)
        is_active: Nuevo estado (opcional)
    """
    usuario_id: int
    nombre_completo: Optional[str] = None
    telefono: Optional[str] = None
    rol_id: Optional[int] = None
    is_active: Optional[bool] = None


@dataclass
class ListarUsuariosDTO:
    """
    DTO para listar usuarios con filtros.
    
    Attributes:
        busqueda: Texto de búsqueda (email, username, nombre)
        rol_id: Filtrar por rol
        is_active: Filtrar por estado
        ordenar_por: Campo para ordenar
        orden: Dirección del orden (asc/desc)
        pagina: Número de página
        por_pagina: Registros por página
    """
    busqueda: Optional[str] = None
    rol_id: Optional[int] = None
    is_active: Optional[bool] = None
    ordenar_por: str = 'fecha_registro'
    orden: str = 'desc'
    pagina: int = 1
    por_pagina: int = 20
