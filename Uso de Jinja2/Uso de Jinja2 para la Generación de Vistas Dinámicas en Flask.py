import os
import json
import uuid
from flask import Flask, render_template, request, redirect, url_for, flash
from redis import Redis
from redis.exceptions import ConnectionError, RedisError
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret-key-123")

# Configuración
class Config:
    KEYDB_HOST = os.getenv("KEYDB_HOST", "localhost")
    KEYDB_PORT = int(os.getenv("KEYDB_PORT", "6379"))
    KEYDB_PASSWORD = os.getenv("KEYDB_PASSWORD", None)

app.config.from_object(Config)

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
            flash(f"Libro '{libro['titulo']}' agregado correctamente", "success")
            return redirect(url_for('index'))
        except RedisError as e:
            flash(f"Error al guardar el libro: {str(e)}", "danger")
    
    estados = ["No leído", "Leyendo", "Leído"]
    return render_template('libros/agregar.html', estados=estados)

@app.route('/libros/editar/<string:libro_id>', methods=['GET', 'POST'])
def editar_libro(libro_id):
    """Edita un libro existente"""
    libro = get_libro(libro_id)
    if not libro:
        flash("Libro no encontrado", "danger")
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        titulo = request.form.get('titulo', '').strip()
        autor = request.form.get('autor', '').strip()
        genero = request.form.get('genero', '').strip()
        estado = request.form.get('estado', 'No leído')
        
        if not titulo or not autor:
            flash("Título y autor son campos obligatorios", "danger")
            return redirect(url_for('editar_libro', libro_id=libro_id))
        
        libro_actualizado = {
            "id": libro_id,
            "titulo": titulo,
            "autor": autor,
            "genero": genero,
            "estado": estado
        }
        
        redis = get_db_connection()
        if not redis:
            return redirect(url_for('index'))
        
        try:
            redis.set(f"libro:{libro_id}", json.dumps(libro_actualizado))
            flash("Libro actualizado correctamente", "success")
            return redirect(url_for('index'))
        except RedisError as e:
            flash(f"Error al actualizar el libro: {str(e)}", "danger")
    
    estados = ["No leído", "Leyendo", "Leído"]
    return render_template('libros/editar.html', libro=libro, estados=estados)

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
            flash(f"Libro '{libro['titulo']}' eliminado correctamente", "success")
            return redirect(url_for('index'))
        except RedisError as e:
            flash(f"Error al eliminar el libro: {str(e)}", "danger")
    
    return render_template('libros/eliminar.html', libro=libro)

@app.route('/libros/buscar', methods=['GET', 'POST'])
def buscar_libros():
    """Busca libros según criterios"""
    if request.method == 'POST':
        titulo = request.form.get('titulo', '').strip()
        autor = request.form.get('autor', '').strip()
        genero = request.form.get('genero', '').strip()
        
        redis = get_db_connection()
        if not redis:
            return render_template('libros/buscar.html', resultados=[])
        
        resultados = []
        for key in redis.scan_iter("libro:*"):
            libro_data = redis.get(key)
            if libro_data:
                libro = json.loads(libro_data)
                coincide = True
                
                if titulo and titulo.lower() not in libro['titulo'].lower():
                    coincide = False
                if autor and autor.lower() not in libro['autor'].lower():
                    coincide = False
                if genero and (not libro.get('genero') or genero.lower() not in libro.get('genero', '').lower()):
                    coincide = False
                
                if coincide:
                    resultados.append(libro)
        
        resultados_ordenados = sorted(resultados, key=lambda x: x["titulo"])
        return render_template('libros/buscar.html', resultados=resultados_ordenados)
    
    return render_template('libros/buscar.html', resultados=None)

if __name__ == '__main__':
    app.run(debug=True)