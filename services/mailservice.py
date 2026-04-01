import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def generar_html_reporte_creacion_ordenes(ordenes_creadas, ordenes_no_creadas):
    """
    Genera un HTML con dos tablas de una sola columna (OrderNumber), 
    una para órdenes exitosas y otra para fallidas.
    """
    try:
        # Función auxiliar para generar las filas de cada tabla
        def generar_filas(lista_ordenes):
            filas = ""
            if not lista_ordenes:
                return """
                <tr style="background-color: #f9f9f9;">
                    <td style="padding: 12px; text-align: center; border-bottom: 1px solid #ddd; color: #777;">Ninguna</td>
                </tr>
                """
                
            for orden in lista_ordenes:
                # Maneja tanto si la lista tiene diccionarios {'OrderNumber': '123'} como si son strings directos '123'
                order_num = orden['OrderNumber'] if isinstance(orden, dict) else orden
                
                filas += f"""
                <tr style="background-color: #f9f9f9;">
                    <td style="padding: 12px; text-align: center; border-bottom: 1px solid #ddd; color: #333;"><b>{order_num}</b></td>
                </tr>
                """
            return filas

        # Generamos las filas de ambas listas
        filas_creadas = generar_filas(ordenes_creadas)
        filas_no_creadas = generar_filas(ordenes_no_creadas)

        # Template principal HTML
        html_message = f"""
        <html>
        <body style="font-family: Arial, sans-serif; background-color: #f4f4f9; padding: 20px;">
            <h1 style="color: #333; font-size: 24px; text-align: center;">Resumen de Integración: DSCO a Mintsoft</h1>

            <h2 style="color: #4CAF50; text-align: center; font-size: 20px; margin-top: 30px;">✅ Órdenes Nuevas Creadas</h2>
            <table style="width: 80%; max-width: 400px; margin: 0 auto; border-collapse: collapse; background: #fff; box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1); border-radius: 10px; overflow: hidden;">
                <tr style="background-color: #4CAF50; color: white;">
                    <th style="padding: 12px; text-align: center; border-bottom: 1px solid #ddd;">OrderNumber</th>
                </tr>
                {filas_creadas}
            </table>

            <h2 style="color: #F44336; text-align: center; font-size: 20px; margin-top: 40px;">❌ Órdenes Nuevas No Creadas</h2>
            <table style="width: 80%; max-width: 400px; margin: 0 auto; border-collapse: collapse; background: #fff; box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1); border-radius: 10px; overflow: hidden;">
                <tr style="background-color: #F44336; color: white;">
                    <th style="padding: 12px; text-align: center; border-bottom: 1px solid #ddd;">OrderNumber</th>
                </tr>
                {filas_no_creadas}
            </table>

            <p style="text-align: center; font-size: 12px; color: #888; margin-top: 30px;">Reporte generado automáticamente</p>
        </body>
        </html>
        """
        return html_message
    except Exception as e:
        print("Error al generar el HTML:", e)
        return ""

def enviar_reporte_email(html_contenido, destinatarios, asunto):
    """
    Envía el email usando SMTP.
    """
    email_sender = os.getenv("EMAIL_USER")
    email_password = os.getenv("EMAIL_PASS")
    smtp_server = "smtp.gmail.com" 
    smtp_port = 587

    msg = MIMEMultipart()
    msg['From'] = email_sender
    
    if isinstance(destinatarios, list):
        msg['To'] = ", ".join(destinatarios)
    else:
        msg['To'] = destinatarios
        
    msg['Subject'] = asunto

    msg.attach(MIMEText(html_contenido, 'html'))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(email_sender, email_password)
        server.send_message(msg)
        server.quit()
        print(f"✅ Mail enviado exitosamente a {destinatarios}")
    except Exception as e:
        print(f"❌ Error al enviar el mail: {e}")