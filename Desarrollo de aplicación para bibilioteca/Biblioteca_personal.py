import sqlite3
from typing import List, Tuple, Optional, Dict, Any
from colorama import init, Fore, Style
from tabulate import tabulate

# Inicializar colorama para colores en la consola
init(autoreset=True)

class Biblioteca:
    """Clase principal que maneja la conexión y operaciones con la base de datos."""
    
    def __init__(self, db_name: str = "biblioteca.db"):
        """Inicializa la biblioteca con una base de datos SQLite.
        
        Args:
            db_name (str): Nombre del archivo de base de datos. Por defecto "biblioteca.db".
        """
        self.db_name = db_name
        self.conn = None
        self.cursor = None
        self.inicializar_bd()

    def inicializar_bd(self) -> None:
        """Inicializa la conexión a la base de datos y crea las tablas si no existen."""
        try:
            self.conn = sqlite3.connect(self.db_name)
            self.cursor = self.conn.cursor()

            # Crear tabla de libros si no existe
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS libros (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    titulo TEXT NOT NULL,
                    autor TEXT NOT NULL,
                    genero TEXT NOT NULL,
                    leido BOOLEAN NOT NULL
                )
            ''')
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"{Fore.RED}Error al inicializar la base de datos: {e}")

    def cerrar_conexion(self) -> None:
        """Cierra la conexión a la base de datos."""
        if self.conn:
            self.conn.close()

    def agregar_libro(self, titulo: str, autor: str, genero: str, leido: bool) -> bool:
        """Agrega un nuevo libro a la biblioteca.
        
        Args:
            titulo (str): Título del libro
            autor (str): Autor del libro
            genero (str): Género del libro
            leido (bool): Estado de lectura (True/False)
            
        Returns:
            bool: True si se agregó correctamente, False si hubo error
        """
        # Validar campos obligatorios
        if not titulo or not autor or not genero:
            print(f"{Fore.RED}Error: Todos los campos son obligatorios.")
            return False

        try:
            self.cursor.execute('''
                INSERT INTO libros (titulo, autor, genero, leido)
                VALUES (?, ?, ?, ?)
            ''', (titulo, autor, genero, leido))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"{Fore.RED}Error al agregar libro: {e}")
            return False

    def actualizar_libro(self, id_libro: int, datos: Dict[str, Any]) -> bool:
        """Actualiza la información de un libro existente.
        
        Args:
            id_libro (int): ID del libro a actualizar
            datos (dict): Diccionario con los campos a actualizar
            
        Returns:
            bool: True si se actualizó correctamente, False si hubo error
        """
        if not datos:
            print(f"{Fore.YELLOW}No hay cambios para actualizar.")
            return False

        try:
            campos = []
            valores = []

            for campo, valor in datos.items():
                campos.append(f"{campo} = ?")
                valores.append(valor)

            valores.append(id_libro)

            consulta = f"UPDATE libros SET {', '.join(campos)} WHERE id = ?"
            self.cursor.execute(consulta, valores)
            self.conn.commit()

            return self.cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"{Fore.RED}Error al actualizar libro: {e}")
            return False

    def eliminar_libro(self, id_libro: int) -> bool:
        """Elimina un libro de la biblioteca.
        
        Args:
            id_libro (int): ID del libro a eliminar
            
        Returns:
            bool: True si se eliminó correctamente, False si hubo error
        """
        try:
            self.cursor.execute("DELETE FROM libros WHERE id = ?", (id_libro,))
            self.conn.commit()
            return self.cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"{Fore.RED}Error al eliminar libro: {e}")
            return False

    def listar_libros(self) -> List[Tuple]:
        """Obtiene todos los libros en la biblioteca.
        
        Returns:
            List[Tuple]: Lista de tuplas con la información de los libros
        """
        try:
            self.cursor.execute("SELECT id, titulo, autor, genero, leido FROM libros ORDER BY titulo")
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"{Fore.RED}Error al listar libros: {e}")
            return []

    def buscar_libros(self, campo: str, valor: str) -> List[Tuple]:
        """Busca libros según un criterio específico.
        
        Args:
            campo (str): Campo por el que buscar (titulo/autor/genero)
            valor (str): Valor a buscar
            
        Returns:
            List[Tuple]: Lista de tuplas con los libros encontrados
        """
        if not valor.strip():
            print(f"{Fore.YELLOW}El término de búsqueda no puede estar vacío.")
            return []

        try:
            if campo not in ['titulo', 'autor', 'genero']:
                print(f"{Fore.RED}Campo de búsqueda no válido")
                return []

            consulta = f"SELECT id, titulo, autor, genero, leido FROM libros WHERE {campo} LIKE ? ORDER BY titulo"
            self.cursor.execute(consulta, (f"%{valor}%",))
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"{Fore.RED}Error al buscar libros: {e}")
            return []

    def obtener_libro_por_id(self, id_libro: int) -> Optional[Tuple]:
        """Obtiene un libro por su ID.
        
        Args:
            id_libro (int): ID del libro a buscar
            
        Returns:
            Optional[Tuple]: Tupla con la información del libro o None si no se encuentra
        """
        try:
            self.cursor.execute("SELECT id, titulo, autor, genero, leido FROM libros WHERE id = ?", (id_libro,))
            return self.cursor.fetchone()
        except sqlite3.Error as e:
            print(f"{Fore.RED}Error al obtener libro: {e}")
            return None

def mostrar_menu() -> None:
    """Muestra el menú principal de la aplicación."""
    print(f"\n{Fore.CYAN}===== BIBLIOTECA PERSONAL ====={Style.RESET_ALL}")
    print(f"{Fore.WHITE}1. Agregar nuevo libro")
    print(f"{Fore.WHITE}2. Actualizar información de un libro")
    print(f"{Fore.WHITE}3. Eliminar libro existente")
    print(f"{Fore.WHITE}4. Ver listado de libros")
    print(f"{Fore.WHITE}5. Buscar libros")
    print(f"{Fore.WHITE}6. Salir")
    print(f"{Fore.CYAN}==============================={Style.RESET_ALL}")

def limpiar_pantalla() -> None:
    """Limpia la pantalla de la consola."""
    print("\033[2J\033[H", end="")

def formatear_libros_tabla(libros: List[Tuple]) -> str:
    """Formatea una lista de libros como una tabla legible.
    
    Args:
        libros (List[Tuple]): Lista de libros a formatear
        
    Returns:
        str: Tabla formateada como string
    """
    if not libros:
        return f"{Fore.YELLOW}No hay libros para mostrar."
    
    tabla_datos = []
    for libro in libros:
        tabla_datos.append([
            libro[0],
            libro[1],
            libro[2],
            libro[3],
            'Sí' if libro[4] else 'No'
        ])
    return tabulate(
        tabla_datos,
        headers=["ID", "Título", "Autor", "Género", "Leído"],
        tablefmt="grid"
    )

def validar_entrada_numerica(mensaje: str, rango: Tuple[int, int] = None) -> Optional[int]:
    """Valida que la entrada sea un número entero dentro de un rango opcional.
    
    Args:
        mensaje (str): Mensaje a mostrar al usuario
        rango (Tuple[int, int], optional): Rango válido (min, max)
        
    Returns:
        Optional[int]: Número validado o None si no es válido
    """
    try:
        numero = int(input(mensaje))
        if rango and (numero < rango[0] or numero > rango[1]):
            print(f"{Fore.RED}Error: El número debe estar entre {rango[0]} y {rango[1]}.")
            return None
        return numero
    except ValueError:
        print(f"{Fore.RED}Error: Ingrese un valor numérico válido.")
        return None

def obtener_estado_lectura() -> bool:
    """Solicita y valida el estado de lectura (leído/no leído).
    
    Returns:
        bool: True si está leído, False si no
    """
    leido_input = input("¿Leído? (s/n): ").lower()
    while leido_input not in ['s', 'n']:
        print(f"{Fore.YELLOW}Respuesta no válida. Utilice 's' para sí o 'n' para no.")
        leido_input = input("¿Leído? (s/n): ").lower()
    return leido_input == 's'

def mostrar_titulo_seccion(titulo: str) -> None:
    """Muestra un título de sección formateado.
    
    Args:
        titulo (str): Título de la sección
    """
    print(f"\n{Fore.CYAN}=== {titulo.upper()} ==={Style.RESET_ALL}")

def main() -> None:
    """Función principal del programa."""
    biblioteca = Biblioteca()

    while True:
        limpiar_pantalla()
        mostrar_menu()

        opcion = validar_entrada_numerica("Seleccione una opción (1-6): ", (1, 6))
        if opcion is None:
            input(f"{Fore.YELLOW}Presione Enter para continuar...")
            continue

        if opcion == 1:  # Agregar nuevo libro
            limpiar_pantalla()
            mostrar_titulo_seccion("Agregar nuevo libro")

            titulo = input("Título: ").strip()
            autor = input("Autor: ").strip()
            genero = input("Género: ").strip()

            # Validar entradas vacías
            if not titulo or not autor or not genero:
                print(f"{Fore.RED}Error: Todos los campos son obligatorios.")
                input(f"{Fore.YELLOW}Presione Enter para continuar...")
                continue

            leido = obtener_estado_lectura()

            if biblioteca.agregar_libro(titulo, autor, genero, leido):
                print(f"\n{Fore.GREEN}¡Libro agregado correctamente!")
            else:
                print(f"\n{Fore.RED}No se pudo agregar el libro.")

        elif opcion == 2:  # Actualizar libro
            limpiar_pantalla()
            mostrar_titulo_seccion("Actualizar libro")

            # Mostrar lista de libros para referencia
            libros = biblioteca.listar_libros()
            if libros:
                print("\nListado de libros:")
                print(formatear_libros_tabla(libros))
                print()

            id_libro = validar_entrada_numerica("ID del libro a actualizar: ")
            if id_libro is None:
                input(f"{Fore.YELLOW}Presione Enter para continuar...")
                continue

            libro = biblioteca.obtener_libro_por_id(id_libro)

            if libro:
                print(f"\n{Fore.WHITE}Libro actual: {libro[1]} - {libro[2]}")
                datos = {}

                nuevo_titulo = input(f"Nuevo título [{libro[1]}]: ").strip()
                if nuevo_titulo: datos['titulo'] = nuevo_titulo

                nuevo_autor = input(f"Nuevo autor [{libro[2]}]: ").strip()
                if nuevo_autor: datos['autor'] = nuevo_autor

                nuevo_genero = input(f"Nuevo género [{libro[3]}]: ").strip()
                if nuevo_genero: datos['genero'] = nuevo_genero

                nuevo_leido = input(f"¿Leído? (s/n) [{('s' if libro[4] else 'n')}]: ").lower()
                if nuevo_leido in ['s', 'n']:
                    datos['leido'] = nuevo_leido == 's'

                if datos and biblioteca.actualizar_libro(id_libro, datos):
                    print(f"\n{Fore.GREEN}¡Libro actualizado correctamente!")
                else:
                    print(f"\n{Fore.YELLOW}No se realizaron cambios al libro.")
            else:
                print(f"\n{Fore.RED}No se encontró un libro con ID {id_libro}")

        elif opcion == 3:  # Eliminar libro
            limpiar_pantalla()
            mostrar_titulo_seccion("Eliminar libro")

            # Mostrar lista de libros para referencia
            libros = biblioteca.listar_libros()
            if libros:
                print("\nListado de libros:")
                print(formatear_libros_tabla(libros))
                print()

            id_libro = validar_entrada_numerica("ID del libro a eliminar: ")
            if id_libro is None:
                input(f"{Fore.YELLOW}Presione Enter para continuar...")
                continue

            libro = biblioteca.obtener_libro_por_id(id_libro)
            if not libro:
                print(f"\n{Fore.RED}No se encontró un libro con ID {id_libro}")
            else:
                confirmacion = input(f"¿Eliminar '{libro[1]}'? (s/n): ").lower()
                while confirmacion not in ['s', 'n']:
                    print(f"{Fore.YELLOW}Respuesta no válida. Utilice 's' para sí o 'n' para no.")
                    confirmacion = input(f"¿Eliminar '{libro[1]}'? (s/n): ").lower()

                if confirmacion == 's':
                    if biblioteca.eliminar_libro(id_libro):
                        print(f"\n{Fore.GREEN}¡Libro eliminado correctamente!")
                    else:
                        print(f"\n{Fore.RED}No se pudo eliminar el libro.")

        elif opcion == 4:  # Listar libros
            limpiar_pantalla()
            mostrar_titulo_seccion("Listado de libros")
            
            libros = biblioteca.listar_libros()
            print(formatear_libros_tabla(libros))

        elif opcion == 5:  # Buscar libros
            limpiar_pantalla()
            mostrar_titulo_seccion("Buscar libros")
            
            print(f"1. Por título\n2. Por autor\n3. Por género")
            opcion_busqueda = validar_entrada_numerica("Opción (1-3): ", (1, 3))
            
            if opcion_busqueda is None:
                input(f"{Fore.YELLOW}Presione Enter para continuar...")
                continue

            campo = ['titulo', 'autor', 'genero'][opcion_busqueda - 1]
            valor = input(f"{campo.capitalize()}: ").strip()

            if not valor:
                print(f"{Fore.RED}El término de búsqueda no puede estar vacío.")
                input(f"{Fore.YELLOW}Presione Enter para continuar...")
                continue

            libros = biblioteca.buscar_libros(campo, valor)
            if libros:
                print(f"\n{Fore.GREEN}Resultados encontrados ({len(libros)}):")
                print(formatear_libros_tabla(libros))
            else:
                print(f"\n{Fore.YELLOW}No se encontraron resultados.")

        elif opcion == 6:  # Salir
            biblioteca.cerrar_conexion()
            print(f"\n{Fore.GREEN}¡Hasta pronto!")
            break

        input(f"\n{Fore.YELLOW}Presione Enter para continuar...")

if __name__ == "__main__":
    main()