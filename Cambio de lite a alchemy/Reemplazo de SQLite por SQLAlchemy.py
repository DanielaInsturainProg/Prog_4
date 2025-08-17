import os
from enum import Enum
from sqlalchemy import create_engine, Column, Integer, String, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from colorama import init, Fore, Style
from tabulate import tabulate
import re

# Inicializar colorama
init(autoreset=True)

# Configuración de la base de datos
DATABASE_URL = "mysql+pymysql://Dani:qwert@localhost:3306/biblioteca"


# Definición del modelo de datos
Base = declarative_base()

class EstadoLectura(Enum):
    """Enumeración para los estados de lectura"""
    NO_LEIDO = "No leído"
    LEYENDO = "Leyendo"
    LEIDO = "Leído"

class Libro(Base):
    """Modelo de datos para los libros"""
    __tablename__ = 'libros'

    id = Column(Integer, primary_key=True)
    titulo = Column(String(100), nullable=False)
    autor = Column(String(100), nullable=False)
    genero = Column(String(50))
    estado = Column(SQLEnum(EstadoLectura), nullable=False, default=EstadoLectura.NO_LEIDO)

    def __repr__(self):
        return f"<Libro(id={self.id}, titulo='{self.titulo}', autor='{self.autor}')>"

class ORM:
    """Clase para manejar las operaciones de base de datos con SQLAlchemy"""
    
    @staticmethod
    def conectar_bd():
        """Crea y retorna el motor de SQLAlchemy"""
        try:
            engine = create_engine(DATABASE_URL, pool_pre_ping=True)
            return engine
        except Exception as e:
            print(f"{Fore.RED}Error al conectar a la base de datos: {e}")
            raise

    @staticmethod
    def obtener_sesion(engine):
        """Crea y retorna una sesión de SQLAlchemy"""
        Session = sessionmaker(bind=engine)
        return Session()

    @staticmethod
    def agregar_libro(session, titulo, autor, genero=None, estado=EstadoLectura.NO_LEIDO):
        """Agrega un nuevo libro a la base de datos"""
        try:
            libro = Libro(
                titulo=titulo,
                autor=autor,
                genero=genero,
                estado=estado
            )
            session.add(libro)
            session.commit()
            return libro
        except Exception as e:
            session.rollback()
            print(f"{Fore.RED}Error al agregar libro: {e}")
            raise

    @staticmethod
    def obtener_todos_libros(session):
        """Obtiene todos los libros de la base de datos"""
        try:
            return session.query(Libro).order_by(Libro.titulo).all()
        except Exception as e:
            print(f"{Fore.RED}Error al obtener libros: {e}")
            raise

    @staticmethod
    def buscar_libros(session, criterios):
        """Busca libros según los criterios proporcionados"""
        try:
            query = session.query(Libro)
            
            if 'titulo' in criterios:
                query = query.filter(Libro.titulo.ilike(f"%{criterios['titulo']}%"))
            if 'autor' in criterios:
                query = query.filter(Libro.autor.ilike(f"%{criterios['autor']}%"))
            if 'genero' in criterios:
                query = query.filter(Libro.genero.ilike(f"%{criterios['genero']}%"))
            
            return query.order_by(Libro.titulo).all()
        except Exception as e:
            print(f"{Fore.RED}Error al buscar libros: {e}")
            raise

    @staticmethod
    def actualizar_libro(session, id_libro, datos):
        """Actualiza un libro existente"""
        try:
            libro = session.query(Libro).filter(Libro.id == id_libro).first()
            if not libro:
                raise ValueError(f"No se encontró libro con ID {id_libro}")
            
            for campo, valor in datos.items():
                setattr(libro, campo, valor)
            
            session.commit()
            return libro
        except Exception as e:
            session.rollback()
            print(f"{Fore.RED}Error al actualizar libro: {e}")
            raise

    @staticmethod
    def eliminar_libro(session, id_libro):
        """Elimina un libro de la base de datos"""
        try:
            libro = session.query(Libro).filter(Libro.id == id_libro).first()
            if libro:
                session.delete(libro)
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            print(f"{Fore.RED}Error al eliminar libro: {e}")
            raise

def mostrar_menu():
    """Muestra el menú principal de la aplicación"""
    print(f"\n{Fore.CYAN}{Style.BRIGHT}===== BIBLIOTECA PERSONAL ====={Style.RESET_ALL}")
    print(f"{Fore.GREEN}1. Agregar nuevo libro")
    print(f"{Fore.GREEN}2. Ver todos los libros")
    print(f"{Fore.GREEN}3. Buscar libros")
    print(f"{Fore.GREEN}4. Actualizar información de libro")
    print(f"{Fore.GREEN}5. Eliminar libro")
    print(f"{Fore.GREEN}6. Salir")

    while True:
        opcion = input(f"{Fore.YELLOW}Seleccione una opción (1-6): ")
        if opcion in ['1', '2', '3', '4', '5', '6']:
            return opcion
        print(f"{Fore.RED}Opción inválida. Intente de nuevo.")

def mostrar_libros(libros):
    """Muestra una lista de libros usando tabulate"""
    if not libros:
        print(f"{Fore.YELLOW}No se encontraron libros.")
        return

    # Preparar datos para tabulate
    headers = ["ID", "TÍTULO", "AUTOR", "GÉNERO", "ESTADO"]
    tabla_datos = []

    for libro in libros:
        titulo = (libro.titulo[:28] + '..') if len(libro.titulo) > 28 else libro.titulo
        autor = (libro.autor[:23] + '..') if len(libro.autor) > 23 else libro.autor
        genero = (libro.genero[:18] + '..') if len(libro.genero) > 18 else libro.genero

        tabla_datos.append([libro.id, titulo, autor, genero, libro.estado.value])

    # Mostrar tabla con tabulate
    print(tabulate(tabla_datos, headers=headers, tablefmt="pretty"))

def validar_entrada(prompt, regex=None, obligatorio=True, mensaje_error=None):
    """Valida la entrada del usuario según patrón y si es obligatoria"""
    while True:
        valor = input(prompt).strip()

        if not valor and not obligatorio:
            return valor

        if not valor and obligatorio:
            print(f"{Fore.RED}Este campo es obligatorio.")
            continue

        if regex and not re.match(regex, valor):
            print(f"{Fore.RED}{mensaje_error or 'Formato inválido'}")
            continue

        return valor

def inicializar_bd(engine):
    """Crea las tablas en la base de datos si no existen"""
    try:
        Base.metadata.create_all(engine)
        print(f"{Fore.GREEN}Base de datos inicializada correctamente.")
    except Exception as e:
        print(f"{Fore.RED}Error al inicializar la base de datos: {e}")
        raise

def main():
    try:
        # Conectar a la base de datos
        print(f"{Fore.CYAN}Conectando a la base de datos...")
        engine = ORM.conectar_bd()
        
        # Inicializar la base de datos (crear tablas si no existen)
        inicializar_bd(engine)
        
        # Obtener sesión
        sesion = ORM.obtener_sesion(engine)
        print(f"{Fore.GREEN}Conexión exitosa.")

        while True:
            opcion = mostrar_menu()

            if opcion == '1':  # Agregar libro
                print(f"\n{Fore.CYAN}{Style.BRIGHT}--- Agregar Nuevo Libro ---{Style.RESET_ALL}")
                titulo = validar_entrada(f"{Fore.YELLOW}Título: ", obligatorio=True)
                autor = validar_entrada(f"{Fore.YELLOW}Autor: ", obligatorio=True)
                genero = validar_entrada(f"{Fore.YELLOW}Género: ", obligatorio=False)

                print(f"\n{Fore.CYAN}Estado de lectura:")
                print(f"{Fore.GREEN}1. No leído")
                print(f"{Fore.GREEN}2. Leyendo")
                print(f"{Fore.GREEN}3. Leído")

                estado_opcion = validar_entrada(
                    f"{Fore.YELLOW}Seleccione estado (1-3): ",
                    regex=r"^[1-3]$",
                    mensaje_error="Opción inválida. Ingrese 1, 2 o 3."
                )

                estados = {
                    '1': EstadoLectura.NO_LEIDO,
                    '2': EstadoLectura.LEYENDO,
                    '3': EstadoLectura.LEIDO
                }
                estado = estados[estado_opcion]

                libro = ORM.agregar_libro(sesion, titulo, autor, genero, estado)
                print(f"\n{Fore.GREEN}Libro '{libro.titulo}' agregado con éxito.")

            elif opcion == '2':  # Ver todos los libros
                print(f"\n{Fore.CYAN}{Style.BRIGHT}--- Todos los Libros ---{Style.RESET_ALL}")
                libros = ORM.obtener_todos_libros(sesion)
                mostrar_libros(libros)

            elif opcion == '3':  # Buscar libros
                print(f"\n{Fore.CYAN}{Style.BRIGHT}--- Búsqueda de Libros ---{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}Deje en blanco para no filtrar por ese campo")
                titulo = input("Título: ")
                autor = input("Autor: ")
                genero = input("Género: ")

                criterios = {}
                if titulo:
                    criterios['titulo'] = titulo
                if autor:
                    criterios['autor'] = autor
                if genero:
                    criterios['genero'] = genero

                libros = ORM.buscar_libros(sesion, criterios)
                mostrar_libros(libros)

            elif opcion == '4':  # Actualizar libro
                print(f"\n{Fore.CYAN}{Style.BRIGHT}--- Actualizar Libro ---{Style.RESET_ALL}")
                id_libro = validar_entrada(
                    f"{Fore.YELLOW}ID del libro a actualizar: ",
                    regex=r"^\d+$",
                    mensaje_error="ID inválido. Ingrese solo números."
                )

                # Verificar si el libro existe
                libro = sesion.query(Libro).filter(Libro.id == id_libro).first()
                if not libro:
                    print(f"{Fore.RED}No se encontró ningún libro con ID {id_libro}.")
                    continue

                print(f"\n{Fore.CYAN}Actualizando libro: {Fore.WHITE}{libro.titulo}")
                print(f"{Fore.YELLOW}Deje en blanco para mantener el valor actual")

                nuevo_titulo = input(f"Título [{libro.titulo}]: ")
                nuevo_autor = input(f"Autor [{libro.autor}]: ")
                nuevo_genero = input(f"Género [{libro.genero}]: ")

                print(f"\n{Fore.CYAN}Estado de lectura actual: {Fore.WHITE}{libro.estado.value}")
                print(f"{Fore.GREEN}1. No leído")
                print(f"{Fore.GREEN}2. Leyendo")
                print(f"{Fore.GREEN}3. Leído")
                print(f"{Fore.GREEN}4. Mantener actual")

                estado_opcion = validar_entrada(
                    f"{Fore.YELLOW}Seleccione nuevo estado (1-4): ",
                    regex=r"^[1-4]$",
                    mensaje_error="Opción inválida. Ingrese un número del 1 al 4."
                )

                datos = {}
                if nuevo_titulo:
                    datos['titulo'] = nuevo_titulo
                if nuevo_autor:
                    datos['autor'] = nuevo_autor
                if nuevo_genero:
                    datos['genero'] = nuevo_genero

                estados = {
                    '1': EstadoLectura.NO_LEIDO,
                    '2': EstadoLectura.LEYENDO,
                    '3': EstadoLectura.LEIDO
                }

                if estado_opcion in estados:
                    datos['estado'] = estados[estado_opcion]

                libro = ORM.actualizar_libro(sesion, id_libro, datos)
                print(f"{Fore.GREEN}Libro actualizado con éxito.")

            elif opcion == '5':  # Eliminar libro
                print(f"\n{Fore.CYAN}{Style.BRIGHT}--- Eliminar Libro ---{Style.RESET_ALL}")
                id_libro = validar_entrada(
                    f"{Fore.YELLOW}ID del libro a eliminar: ",
                    regex=r"^\d+$",
                    mensaje_error="ID inválido. Ingrese solo números."
                )

                # Verificar si el libro existe
                libro = sesion.query(Libro).filter(Libro.id == id_libro).first()
                if not libro:
                    print(f"{Fore.RED}No se encontró ningún libro con ID {id_libro}.")
                    continue

                confirmacion = validar_entrada(
                    f"{Fore.RED}¿Está seguro de eliminar '{libro.titulo}'? (s/n): ",
                    regex=r"^[sSnN]$",
                    mensaje_error="Respuesta inválida. Ingrese 's' o 'n'."
                )

                if confirmacion.lower() == 's':
                    if ORM.eliminar_libro(sesion, id_libro):
                        print(f"{Fore.GREEN}Libro eliminado con éxito.")
                    else:
                        print(f"{Fore.RED}Error al eliminar el libro.")
                else:
                    print(f"{Fore.YELLOW}Operación cancelada.")

            elif opcion == '6':  # Salir
                print(f"{Fore.CYAN}Saliendo del programa...")
                break

    except Exception as e:
        print(f"{Fore.RED}Error: {e}")
    finally:
        if 'sesion' in locals():
            sesion.close()
        if 'engine' in locals():
            engine.dispose()
        print(f"{Fore.CYAN}Programa finalizado.")

if __name__ == "__main__":
    main()