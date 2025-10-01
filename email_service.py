import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class EmailService:
    def __init__(self):
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.sender_email = "jeanmillosyeye@gmail.com"  # Cambia esto por tu correo
        self.sender_password = "iptv hpgp jueb xout"  # Cambia esto por tu contraseña de aplicación de Gmail

    def enviar_correo_recuperacion(self, destinatario, token):
        try:
            mensaje = MIMEMultipart()
            mensaje["From"] = self.sender_email
            mensaje["To"] = destinatario
            mensaje["Subject"] = "Recuperación de Contraseña - Restaurant JP"

            cuerpo = f"""
            <html>
            <body>
                <h2>Recuperación de Contraseña</h2>
                <p>Has solicitado restablecer tu contraseña.</p>
                <p>Tu código de verificación es: <strong>{token}</strong></p>
                <p>Si no solicitaste este cambio, por favor ignora este correo.</p>
            </body>
            </html>
            """

            mensaje.attach(MIMEText(cuerpo, "html"))

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as servidor:
                servidor.starttls()
                servidor.login(self.sender_email, self.sender_password)
                servidor.send_message(mensaje)

            return {"status": "success", "message": "Correo enviado exitosamente"}
        except Exception as e:
            return {"status": "error", "message": f"Error al enviar el correo: {str(e)}"}