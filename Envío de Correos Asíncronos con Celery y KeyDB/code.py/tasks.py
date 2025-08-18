from code import celery, mail
from flask import render_template
from flask_mail import Message

@celery.task(bind=True, name='enviar_correo_agregado')
def enviar_correo_agregado(self, titulo, autor, ip):
    """Tarea Celery para enviar correo cuando se agrega un libro"""
    try:
        # Renderizar plantilla HTML del correo
        html = render_template(
            'emails/libro_agregado.html',
            titulo=titulo,
            autor=autor,
            ip=ip
        )
        
        # Crear mensaje
        msg = Message(
            subject="Confirmación: Libro agregado a tu biblioteca",
            recipients=["usuario@example.com"],  # Reemplazar con email real
            html=html
        )
        
        # Enviar correo
        mail.send(msg)
        return True
    except Exception as e:
        self.retry(exc=e, countdown=60, max_retries=3)

@celery.task(bind=True, name='enviar_correo_eliminado')
def enviar_correo_eliminado(self, titulo, autor, ip):
    """Tarea Celery para enviar correo cuando se elimina un libro"""
    try:
        # Renderizar plantilla HTML del correo
        html = render_template(
            'emails/libro_eliminado.html',
            titulo=titulo,
            autor=autor,
            ip=ip
        )
        
        # Crear mensaje
        msg = Message(
            subject="Confirmación: Libro eliminado de tu biblioteca",
            recipients=["usuario@example.com"],  # Reemplazar con email real
            html=html
        )
        
        # Enviar correo
        mail.send(msg)
        return True
    except Exception as e:
        self.retry(exc=e, countdown=60, max_retries=3)