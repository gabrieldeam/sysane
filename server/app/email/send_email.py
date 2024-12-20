from fastapi import HTTPException
from email.message import EmailMessage
import smtplib
import os
from jinja2 import Template
from dotenv import load_dotenv

load_dotenv()

MAIL_HOST = os.getenv("MAIL_HOST")
MAIL_PORT = int(os.getenv("MAIL_PORT"))
MAIL_USERNAME = os.getenv("MAIL_USERNAME")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "True").lower() == "true"

def send_verification_email(to_email: str, name: str, verification_url: str):
    try:
        # Carregar o template
        template_path = "app/email/templates/verification_email.html"
        with open(template_path, "r") as f:
            template = Template(f.read())
        content = template.render(name=name, verification_url=verification_url)

        # Configurar a mensagem
        message = EmailMessage()
        message["Subject"] = "Verifique seu email para acessar o Sysane"
        message["From"] = MAIL_USERNAME
        message["To"] = to_email
        message.set_content(content, subtype="html")

        # Conectar ao servidor SMTP
        with smtplib.SMTP(MAIL_HOST, MAIL_PORT) as server:
            if MAIL_USE_TLS:
                server.starttls()
            server.login(MAIL_USERNAME, MAIL_PASSWORD)
            server.send_message(message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Falha ao enviar email: {str(e)}")
