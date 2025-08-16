import sqlite3
import os

def crear_base_datos():
    # Eliminar base de datos existente si existe
    if os.path.exists('aventuras.db'):
        os.remove('aventuras.db')

    # Conectar a la base de datos (la crea si no existe)
    conn = sqlite3.connect('aventuras.db')
    cursor = conn.cursor()

    # Crear tabla de héroes con restricciones mejoradas
    cursor.execute('''
    CREATE TABLE heroes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL UNIQUE,
        clase TEXT NOT NULL CHECK(clase IN ('Guerrero', 'Mago', 'Arquero', 'Clerigo', 'Ladron')),
        nivel_experiencia INTEGER NOT NULL CHECK(nivel_experiencia BETWEEN 1 AND 20)
    )
    ''')

    # Crear tabla de misiones con restricciones mejoradas
    cursor.execute('''
    CREATE TABLE misiones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        nivel_dificultad INTEGER NOT NULL CHECK(nivel_dificultad BETWEEN 1 AND 10),
        localizacion TEXT NOT NULL,
        recompensa INTEGER NOT NULL CHECK(recompensa >= 0),
        fecha_inicio DATE,
        fecha_fin DATE,
        CHECK (fecha_fin IS NULL OR fecha_fin >= fecha_inicio)
    )
    ''')

    # Crear tabla de monstruos con restricciones mejoradas
    cursor.execute('''
    CREATE TABLE monstruos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        tipo TEXT NOT NULL,
        nivel_amenaza INTEGER NOT NULL CHECK(nivel_amenaza BETWEEN 1 AND 10),
        descripcion TEXT
    )
    ''')

    # Crear tabla de unión misiones_heroes con restricciones mejoradas
    cursor.execute('''
    CREATE TABLE misiones_heroes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        mision_id INTEGER NOT NULL,
        heroe_id INTEGER NOT NULL,
        fecha_participacion DATE DEFAULT CURRENT_DATE,
        FOREIGN KEY (mision_id) REFERENCES misiones (id) ON DELETE CASCADE,
        FOREIGN KEY (heroe_id) REFERENCES heroes (id) ON DELETE CASCADE,
        UNIQUE(mision_id, heroe_id)
    )
    ''')

    # Crear tabla de unión misiones_monstruos con restricciones mejoradas
    cursor.execute('''
    CREATE TABLE misiones_monstruos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        mision_id INTEGER NOT NULL,
        monstruo_id INTEGER NOT NULL,
        cantidad INTEGER DEFAULT 1 CHECK(cantidad > 0),
        FOREIGN KEY (mision_id) REFERENCES misiones (id) ON DELETE CASCADE,
        FOREIGN KEY (monstruo_id) REFERENCES monstruos (id) ON DELETE CASCADE,
        UNIQUE(mision_id, monstruo_id)
    )
    ''')

    # Insertar datos de prueba mejorados
    insertar_datos_ficticios(cursor)

    # Crear índices para mejorar el rendimiento
    cursor.execute('CREATE INDEX idx_heroes_nombre ON heroes(nombre)')
    cursor.execute('CREATE INDEX idx_misiones_dificultad ON misiones(nivel_dificultad)')
    cursor.execute('CREATE INDEX idx_monstruos_tipo ON monstruos(tipo)')

    # Confirmar cambios y cerrar conexión
    conn.commit()
    conn.close()

    print("¡Base de datos 'aventuras.db' creada correctamente con todas las tablas, relaciones y datos de prueba!")

def insertar_datos_ficticios(cursor):
    # Insertar héroes con más variedad
    heroes = [
        ('Aragorn', 'Guerrero', 15),
        ('Gandalf', 'Mago', 20),
        ('Legolas', 'Arquero', 18),
        ('Frodo', 'Ladron', 8),
        ('Galadriel', 'Mago', 19),
        ('Gimli', 'Guerrero', 16),
        ('Boromir', 'Guerrero', 14),
        ('Sam', 'Ladron', 7)
    ]
    cursor.executemany("INSERT INTO heroes (nombre, clase, nivel_experiencia) VALUES (?, ?, ?)", heroes)

    # Insertar misiones con más detalles
    misiones = [
        ('Rescate en la Montaña', 5, 'Montañas Nubladas', 500, '2023-01-10', '2023-01-15'),
        ('Tesoro Perdido', 3, 'Bosque Encantado', 300, '2023-02-05', '2023-02-08'),
        ('Batalla Final', 10, 'Mordor', 1000, '2023-03-01', '2023-03-10'),
        ('Escolta de Mercaderes', 2, 'Camino Real', 200, '2023-01-20', '2023-01-22'),
        ('Caza del Dragón', 8, 'Montañas Solitarias', 800, '2023-04-01', '2023-04-05'),
        ('Exploración de Ruinas', 4, 'Ruinas Antiguas', 350, '2023-02-15', '2023-02-18')
    ]
    cursor.executemany("INSERT INTO misiones (nombre, nivel_dificultad, localizacion, recompensa, fecha_inicio, fecha_fin) VALUES (?, ?, ?, ?, ?, ?)", misiones)

    # Insertar monstruos con más variedad
    monstruos = [
        ('Smaug', 'Dragón', 10, 'Dragón dorado que custodia un tesoro'),
        ('Orco Capitán', 'Orco', 5, 'Líder de una banda de orcos'),
        ('Rey Brujo', 'No-muerto', 9, 'Espíritu maligno de gran poder'),
        ('Trasgo', 'Goblin', 2, 'Criatura pequeña pero numerosa'),
        ('Araña Gigante', 'Bestia', 6, 'Araña de tamaño descomunal'),
        ('Balrog', 'Demonio', 10, 'Ser de fuego y sombra'),
        ('Huargo', 'Bestia', 3, 'Lobo gigante y feroz'),
        ('Troll', 'Gigante', 7, 'Criatura grande y fuerte pero torpe')
    ]
    cursor.executemany("INSERT INTO monstruos (nombre, tipo, nivel_amenaza, descripcion) VALUES (?, ?, ?, ?)", monstruos)

    # Insertar relaciones misión-héroe
    misiones_heroes = [
        (1, 1, '2023-01-10'),  # Aragorn en Rescate
        (1, 3, '2023-01-10'),  # Legolas en Rescate
        (2, 4, '2023-02-05'),  # Frodo en Tesoro Perdido
        (3, 1, '2023-03-01'),  # Aragorn en Batalla Final
        (3, 2, '2023-03-01'),  # Gandalf en Batalla Final
        (3, 3, '2023-03-01'),  # Legolas en Batalla Final
        (4, 4, '2023-01-20'),  # Frodo en Escolta
        (4, 5, '2023-01-20'),  # Galadriel en Escolta
        (5, 2, '2023-04-01'),  # Gandalf en Caza del Dragón
        (5, 6, '2023-04-01'),  # Gimli en Caza del Dragón
        (6, 7, '2023-02-15'),  # Boromir en Exploración
        (6, 8, '2023-02-15')   # Sam en Exploración
    ]
    cursor.executemany("INSERT INTO misiones_heroes (mision_id, heroe_id, fecha_participacion) VALUES (?, ?, ?)", misiones_heroes)

    # Insertar relaciones misión-monstruo
    misiones_monstruos = [
        (1, 2, 3),  # 3 Orco Capitán en Rescate
        (1, 4, 10), # 10 Trasgos en Rescate
        (2, 5, 2),  # 2 Arañas Gigantes en Tesoro Perdido
        (3, 1, 1),  # 1 Smaug en Batalla Final
        (3, 3, 1),  # 1 Rey Brujo en Batalla Final
        (4, 4, 5),  # 5 Trasgos en Escolta
        (5, 1, 1),  # 1 Smaug en Caza del Dragón
        (6, 7, 3),  # 3 Huargos en Exploración
        (6, 4, 8)   # 8 Trasgos en Exploración
    ]
    cursor.executemany("INSERT INTO misiones_monstruos (mision_id, monstruo_id, cantidad) VALUES (?, ?, ?)", misiones_monstruos)

def main():
    crear_base_datos()

if __name__ == "__main__":
    main()