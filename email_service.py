import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import uuid
import time
from email.utils import formatdate, make_msgid

class EmailService:
    def __init__(self):
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.sender_email = "jeanmillosyeye@gmail.com"  # Cambia esto por tu correo
        self.sender_password = "iptv hpgp jueb xout"  # Cambia esto por tu contraseña de aplicación de Gmail
        
    def generate_message_id(self):
        """Genera un Message-ID único para cada correo"""
        unique_id = str(uuid.uuid4().hex)
        domain = self.sender_email.split('@')[1]
        return f"{unique_id}@{domain}"
        
    def create_text_version(self, html_content):
        """Crea una versión en texto plano del correo HTML"""
        # Eliminar etiquetas HTML básicas
        text = html_content.replace('<br>', '\n')
        text = text.replace('</p>', '\n')
        text = text.replace('</div>', '\n')
        text = text.replace('</h1>', '\n')
        text = text.replace('</h2>', '\n')
        text = text.replace('</h3>', '\n')
        text = text.replace('</tr>', '\n')
        text = text.replace('</td>', ' ')
        
        # Eliminar todas las demás etiquetas HTML
        import re
        text = re.sub('<[^<]+?>', '', text)
        
        # Eliminar múltiples líneas en blanco
        text = re.sub(r'\n\s*\n', '\n\n', text)
        
        return text.strip()

    def enviar_correo_bienvenida(self, destinatario, nombre):
        try:
            mensaje = MIMEMultipart('alternative')
            # Usar formato RFC 822 para el From
            mensaje["From"] = f"Restaurant JP Gourmet <{self.sender_email}>"
            mensaje["To"] = destinatario
            mensaje["Subject"] = "¡Bienvenido a Restaurant JP Gourmet!"
            # Agregar headers importantes para evitar spam
            mensaje["Reply-To"] = self.sender_email
            mensaje["Message-ID"] = f"<{self.generate_message_id()}>"
            mensaje["List-Unsubscribe"] = f"<mailto:{self.sender_email}?subject=unsubscribe>"
            # Agregar headers de prioridad
            mensaje["Importance"] = "High"
            mensaje["X-Priority"] = "1"

            cuerpo = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        line-height: 1.6;
                        color: #333333;
                        margin: 0;
                        padding: 0;
                    }}
                    .container {{
                        max-width: 600px;
                        margin: 0 auto;
                        padding: 20px;
                        background-color: #f8f9fa;
                    }}
                    .header {{
                        background-color: #B8860B;
                        color: white;
                        text-align: center;
                        padding: 20px;
                        border-radius: 5px 5px 0 0;
                    }}
                    .content {{
                        background-color: white;
                        padding: 30px;
                        border-radius: 0 0 5px 5px;
                        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                    }}
                    .welcome-banner {{
                        background-color: #B8860B;
                        color: white;
                        text-align: center;
                        padding: 30px;
                        margin: -30px -30px 20px -30px;
                        border-bottom: 3px solid #8B6508;
                    }}
                    .benefits {{
                        margin: 20px 0;
                        padding: 20px;
                        background-color: #f8f9fa;
                        border-radius: 5px;
                    }}
                    .benefit-item {{
                        margin: 10px 0;
                        display: flex;
                        align-items: center;
                    }}
                    .benefit-icon {{
                        margin-right: 10px;
                        font-size: 20px;
                    }}
                    .cta-button {{
                        display: inline-block;
                        background-color: #B8860B;
                        color: white;
                        padding: 15px 30px;
                        text-decoration: none;
                        border-radius: 5px;
                        margin: 20px 0;
                        font-weight: bold;
                    }}
                    .social-links {{
                        text-align: center;
                        margin-top: 20px;
                        padding-top: 20px;
                        border-top: 1px solid #ddd;
                    }}
                    .footer {{
                        text-align: center;
                        margin-top: 20px;
                        font-size: 12px;
                        color: #666;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🍽️ Restaurant JP Gourmet</h1>
                    </div>
                    <div class="content">
                        <div class="welcome-banner">
                            <h1>¡Bienvenido, {nombre}!</h1>
                            <p>Gracias por unirte a nuestra familia gastronómica</p>
                        </div>

                        <p>Nos complace darte la bienvenida a Restaurant JP Gourmet, donde la excelencia culinaria se encuentra con la hospitalidad excepcional.</p>

                        <div class="benefits">
                            <h3>Como miembro, podrás disfrutar de:</h3>
                            <div class="benefit-item">
                                <span class="benefit-icon">🎉</span>
                                <span>Reservas prioritarias en nuestro restaurante</span>
                            </div>
                            <div class="benefit-item">
                                <span class="benefit-icon">🌟</span>
                                <span>Acceso a eventos especiales y degustaciones</span>
                            </div>
                            <div class="benefit-item">
                                <span class="benefit-icon">📱</span>
                                <span>Sistema de reservas en línea fácil de usar</span>
                            </div>
                            <div class="benefit-item">
                                <span class="benefit-icon">🎂</span>
                                <span>Sorpresas especiales en fechas importantes</span>
                            </div>
                        </div>

                        <center>
                            <a href="http://localhost:5000/login" class="cta-button">
                                Inicia Sesión Ahora
                            </a>
                        </center>

                        <div class="social-links">
                            <p>Síguenos en nuestras redes sociales:</p>
                            <p>📱 Instagram | 📘 Facebook | 🐦 Twitter</p>
                        </div>

                        <div class="footer">
                            <p>Este correo fue enviado a {destinatario}</p>
                            <p>© 2025 Restaurant JP Gourmet. Todos los derechos reservados.</p>
                        </div>
                    </div>
                </div>
            </body>
            </html>
            """

            # Agregar versión texto plano
            text_version = self.create_text_version(cuerpo)
            mensaje.attach(MIMEText(text_version, 'plain', 'utf-8'))
            
            # Agregar versión HTML
            mensaje.attach(MIMEText(cuerpo, 'html', 'utf-8'))
            
            # Configurar fecha
            mensaje["Date"] = formatdate(localtime=True)

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as servidor:
                servidor.ehlo()  # Identificarse con el servidor
                servidor.starttls()  # Activar encriptación
                servidor.ehlo()  # Re-identificarse sobre TLS
                servidor.login(self.sender_email, self.sender_password)
                
                # Agregar delay para evitar límites de envío
                time.sleep(1)
                
                servidor.send_message(mensaje)

            return {"status": "success", "message": "Correo de bienvenida enviado exitosamente"}
        except Exception as e:
            return {"status": "error", "message": f"Error al enviar el correo: {str(e)}"}

    def enviar_correo_recuperacion(self, destinatario, token):
        try:
            mensaje = MIMEMultipart('alternative')
            mensaje["From"] = f"Restaurant JP Gourmet <{self.sender_email}>"
            mensaje["To"] = destinatario
            mensaje["Subject"] = "Recuperación de Contraseña - Restaurant JP"
            mensaje["Reply-To"] = self.sender_email
            mensaje["Message-ID"] = f"<{self.generate_message_id()}>"
            mensaje["List-Unsubscribe"] = f"<mailto:{self.sender_email}?subject=unsubscribe>"
            mensaje["Importance"] = "High"
            mensaje["X-Priority"] = "1"
            mensaje["Date"] = formatdate(localtime=True)

            cuerpo = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        line-height: 1.6;
                        color: #333333;
                        margin: 0;
                        padding: 0;
                    }}
                    .container {{
                        max-width: 600px;
                        margin: 0 auto;
                        padding: 20px;
                        background-color: #f8f9fa;
                    }}
                    .header {{
                        background-color: #B8860B;
                        color: white;
                        text-align: center;
                        padding: 20px;
                        border-radius: 5px 5px 0 0;
                    }}
                    .content {{
                        background-color: white;
                        padding: 30px;
                        border-radius: 0 0 5px 5px;
                        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                    }}
                    .token {{
                        background-color: #f8f9fa;
                        border: 2px solid #B8860B;
                        color: #B8860B;
                        font-size: 24px;
                        font-weight: bold;
                        padding: 15px;
                        margin: 20px 0;
                        text-align: center;
                        border-radius: 5px;
                        letter-spacing: 5px;
                    }}
                    .warning {{
                        font-size: 12px;
                        color: #666;
                        text-align: center;
                        margin-top: 20px;
                        font-style: italic;
                    }}
                    .logo {{
                        text-align: center;
                        margin-bottom: 20px;
                    }}
                    .logo img {{
                        max-width: 150px;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Restaurante JP</h1>
                    </div>
                    <div class="content">
                        <div class="logo">
                            <h2>🍽️ Restaurante JP Gourmet</h2>
                        </div>
                        <h2 style="color: #B8860B; text-align: center;">Recuperación de Contraseña</h2>
                        <p>Hola,</p>
                        <p>Has solicitado restablecer tu contraseña. Usa el siguiente código de verificación para completar el proceso:</p>
                        
                        <div class="token">
                            {token}
                        </div>
                        
                        <p>Para cambiar tu contraseña:</p>
                        <ol>
                            <li>Ingresa a tu cuenta usando este código como contraseña temporal</li>
                            <li>Se te pedirá crear una nueva contraseña</li>
                            <li>Una vez cambiada, podrás acceder normalmente a tu cuenta</li>
                        </ol>

                        <p class="warning">
                            ⚠️ Si no solicitaste este cambio, por favor ignora este correo y contacta con soporte si tienes alguna inquietud.
                        </p>
                    </div>
                </div>
            </body>
            </html>
            """

            # Agregar versión texto plano
            text_version = self.create_text_version(cuerpo)
            mensaje.attach(MIMEText(text_version, 'plain', 'utf-8'))
            
            # Agregar versión HTML
            mensaje.attach(MIMEText(cuerpo, 'html', 'utf-8'))

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as servidor:
                servidor.ehlo()
                servidor.starttls()
                servidor.ehlo()
                servidor.login(self.sender_email, self.sender_password)
                
                # Agregar delay para evitar límites de envío
                time.sleep(1)
                
                servidor.send_message(mensaje)

            return {"status": "success", "message": "Correo enviado exitosamente"}
        except Exception as e:
            return {"status": "error", "message": f"Error al enviar el correo: {str(e)}"}