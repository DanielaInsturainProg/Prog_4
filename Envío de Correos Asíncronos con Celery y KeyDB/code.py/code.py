import os
import json
import uuid
from flask import Flask, render_template, request, redirect, url_for, flash, current_app
from flask_mail import Mail, Message
from redis import Redis
from redis.exceptions import ConnectionError, RedisError
from dotenv import load_dotenv
from celery import Celery

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret-key-123")

# Configuración
class Config:
    KEYDB_HOST = os.getenv("KEYDB_HOST", "localhost")
    KEYDB_PORT = int(os.getenv("KEYDB_PORT", "6379"))
    KEYDB_PASSWORD = os.getenv("KEYDB_PASSWORD", None)
    
    # Configuración de email
    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.getenv("MAIL_PORT", 587))
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "True") == "True"
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER", "noreply@biblioteca.com")
    
    # Configuración Celery
    CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
    CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/1")

app.config.from_object(Config)

# Inicializar Flask-Mail
mail = Mail(app)

def get_db_connection():
    """Establece conexión con KeyDB"""
    try:
        redis = Redis(
            host=app.config['KEYDB_HOST'],
            port=app.config['KEYDB_PORT'],
            password=app.config['KEYDB_PASSWORD'],
            decode_responses=True
        )
        redis.ping()
        return redis
    except ConnectionError:
        flash("Error al conectar con la base de datos", "danger")
        return None

def get_libro(libro_id: str) -> dict:
    """Obtiene un libro por su ID"""
    redis = get_db_connection()
    if not redis:
        return None
    
    libro_data = redis.get(f"libro:{libro_id}")
    return json.loads(libro_data) if libro_data else None

def make_celery(app):
    """Crea una instancia de Celery configurada con la aplicación Flask"""
    celery = Celery(
        app.import_name,
        broker=app.config['CELERY_BROKER_URL'],
        backend=app.config['CELERY_RESULT_BACKEND']
    )
    celery.conf.update(app.config)
    
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    
    celery.Task = ContextTask
    return celery

# Crear instancia de Celery
celery = make_celery(app)

@app.route('/')
def index():
    """Página principal que lista todos los libros"""
    redis = get_db_connection()
    if not redis:
        return render_template('libros/listar.html', libros=[])
    
    libros = []
    for key in redis.scan_iter("libro:*"):
        libro_data = redis.get(key)
        if libro_data:
            libros.append(json.loads(libro_data))
    
    libros_ordenados = sorted(libros, key=lambda x: x["titulo"])
    return render_template('libros/listar.html', libros=libros_ordenados)

@app.route('/libros/agregar', methods=['GET', 'POST'])
def agregar_libro():
    """Agrega un nuevo libro"""
    if request.method == 'POST':
        titulo = request.form.get('titulo', '').strip()
        autor = request.form.get('autor', '').strip()
        genero = request.form.get('genero', '').strip()
        estado = request.form.get('estado', 'No leído')
        
        if not titulo or not autor:
            flash("Título y autor son campos obligatorios", "danger")
            return redirect(url_for('agregar_libro'))
        
        libro = {
            "id": str(uuid.uuid4()),
            "titulo": titulo,
            "autor": autor,
            "genero": genero,
            "estado": estado
        }
        
        redis = get_db_connection()
        if not redis:
            return redirect(url_for('index'))
        
        try:
            redis.set(f"libro:{libro['id']}", json.dumps(libro))
           
            # Enviar correo de confirmación de forma asíncrona
            enviar_correo_agregado.delay(
                libro['titulo'],
                libro['autor'],
                request.remote_addr
            )
            
            flash(f"Libro '{libro['titulo']}' agregado correctamente", "success")
            return redirect(url_for('index'))
        except RedisError as e:
            flash(f"Error al guardar el libro: {str(e)}", "danger")
    
    estados = ["No leído", "Leyendo", "Leído"]
    return render_template('libros/agregar.html', estados=estados)

@app.route('/libros/eliminar/<string:libro_id>', methods=['GET', 'POST'])
def eliminar_libro(libro_id):
    """Elimina un libro con confirmación"""
    libro = get_libro(libro_id)
    if not libro:
        flash("Libro no encontrado", "danger")
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        redis = get_db_connection()
        if not redis:
            return redirect(url_for('index'))
        
        try:
            redis.delete(f"libro:{libro_id}")
            
            # Enviar correo de confirmación de forma asíncrona
            enviar_correo_eliminado.delay(
                libro['titulo'],
                libro['autor'],
                request.remote_addr
            )
            
            flash(f"Libro '{libro['titulo']}' eliminado correctamente", "success")
            return redirect(url_for('index'))
        except RedisError as e:
            flash(f"Error al eliminar el libro: {str(e)}", "danger")
    
    return render_template('libros/eliminar.html', libro=libro)

# Las rutas editar_libro y buscar_libros permanecen igual que en la versión anterior
# ...

if __name__ == '__main__':
    app.run(debug=True)