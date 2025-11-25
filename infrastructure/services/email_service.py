"""
Servicio de Email - Capa de Infraestructura.

Envía emails para recuperación de contraseña y notificaciones.
"""
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags


class EmailService:
    """
    Servicio para envío de emails.
    
    Responsabilidad única: enviar emails del sistema.
    """
    
    @staticmethod
    def enviar_recuperacion_password(
        email: str,
        nombre: str,
        token: str,
        url_base: str
    ) -> bool:
        """
        Envía email de recuperación de contraseña.
        
        Args:
            email: Email del destinatario
            nombre: Nombre del usuario
            token: Token de recuperación
            url_base: URL base del sitio
            
        Returns:
            True si se envió correctamente
            
        Example:
            >>> service = EmailService()
            >>> enviado = service.enviar_recuperacion_password(
            ...     "usuario@example.com",
            ...     "Juan",
            ...     "token123",
            ...     "http://localhost:8000"
            ... )
        """
        try:
            # URL de recuperación
            url_recuperacion = f"{url_base}/auth/restablecer-password/{token}"
            
            # Asunto
            asunto = "Recuperación de Contraseña - POS Restaurante"
            
            # Mensaje HTML
            mensaje_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        line-height: 1.6;
                        color: #333;
                    }}
                    .container {{
                        max-width: 600px;
                        margin: 0 auto;
                        padding: 20px;
                    }}
                    .button {{
                        display: inline-block;
                        padding: 12px 24px;
                        background-color: #007bff;
                        color: white;
                        text-decoration: none;
                        border-radius: 4px;
                        margin: 20px 0;
                    }}
                    .footer {{
                        margin-top: 30px;
                        font-size: 12px;
                        color: #666;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h2>Hola {nombre},</h2>
                    <p>Recibimos una solicitud para restablecer tu contraseña.</p>
                    <p>Haz clic en el siguiente botón para crear una nueva contraseña:</p>
                    <a href="{url_recuperacion}" class="button">Restablecer Contraseña</a>
                    <p>O copia y pega este enlace en tu navegador:</p>
                    <p>{url_recuperacion}</p>
                    <p><strong>Este enlace expirará en 1 hora.</strong></p>
                    <p>Si no solicitaste este cambio, puedes ignorar este email.</p>
                    <div class="footer">
                        <p>Este es un email automático, por favor no respondas.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Mensaje texto plano (fallback)
            mensaje_texto = f"""
            Hola {nombre},
            
            Recibimos una solicitud para restablecer tu contraseña.
            
            Visita el siguiente enlace para crear una nueva contraseña:
            {url_recuperacion}
            
            Este enlace expirará en 1 hora.
            
            Si no solicitaste este cambio, puedes ignorar este email.
            
            ---
            Este es un email automático, por favor no respondas.
            """
            
            # Enviar email
            send_mail(
                subject=asunto,
                message=mensaje_texto,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                html_message=mensaje_html,
                fail_silently=False
            )
            
            return True
            
        except Exception as e:
            # Log del error (en producción usar logging adecuado)
            print(f"Error al enviar email: {e}")
            return False
    
    @staticmethod
    def enviar_bienvenida(email: str, nombre: str, username: str) -> bool:
        """
        Envía email de bienvenida a nuevo usuario.
        
        Args:
            email: Email del destinatario
            nombre: Nombre del usuario
            username: Username asignado
            
        Returns:
            True si se envió correctamente
        """
        try:
            asunto = "¡Bienvenido al Sistema POS!"
            
            mensaje_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
            </head>
            <body>
                <h2>¡Bienvenido {nombre}!</h2>
                <p>Tu cuenta ha sido creada exitosamente.</p>
                <p><strong>Usuario:</strong> {username}</p>
                <p>Ya puedes iniciar sesión en el sistema.</p>
            </body>
            </html>
            """
            
            mensaje_texto = f"""
            ¡Bienvenido {nombre}!
            
            Tu cuenta ha sido creada exitosamente.
            Usuario: {username}
            
            Ya puedes iniciar sesión en el sistema.
            """
            
            send_mail(
                subject=asunto,
                message=mensaje_texto,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                html_message=mensaje_html,
                fail_silently=False
            )
            
            return True
            
        except Exception as e:
            print(f"Error al enviar email de bienvenida: {e}")
            return False
