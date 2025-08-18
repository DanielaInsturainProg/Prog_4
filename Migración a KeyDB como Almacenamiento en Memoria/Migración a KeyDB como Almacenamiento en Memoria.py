import os
import json
import uuid
from typing import List, Dict, Optional
from redis import Redis
from redis.exceptions import ConnectionError, RedisError
from colorama import init, Fore, Style
from tabulate import tabulate
from dotenv import load_dotenv

# Inicializar colorama
init(autoreset=True)

# Cargar variables de entorno
load_dotenv()

class BibliotecaKeyDB:
    """Clase para manejar las operaciones con KeyDB"""
    
    def __init__(self):
        """Inicializa la conexión con KeyDB"""
        try:
            # Conexión a KeyDB (usando variables de entorno)
            self.redis = Redis(
                host=os.getenv("KEYDB_HOST", "localhost"),
                port=int(os.getenv("KEYDB_PORT", "6379")),
                password=os.getenv("KEYDB_PASSWORD", None),
                decode_responses=True
            )
            # Verificar conexión
            self.redis.ping()
            print(f"{Fore.GREEN}Conexión exitosa a KeyDB")
        except ConnectionError as e:
            print(f"{Fore.RED}Error al conectar a KeyDB: {e}")
            raise

    def generar_id(self) -> str:
        """Genera un ID único para un libro"""
        return str(uuid.uuid4())

    def agregar_libro(self, titulo: str, autor: str, genero: str, estado: str) -> Dict:
        """Agrega un nuevo libro a KeyDB"""
        libro = {
            "id": self.generar_id(),
            "titulo": titulo,
            "autor": autor,
            "genero": genero,
            "estado": estado
        }
        
        try:
            # Almacenar como JSON string
            self.redis.set(f"libro:{libro['id']}", json.dumps(libro))
            return libro
        except RedisError as e:
            print(f"{Fore.RED}Error al agregar libro: {e}")
            raise

    def obtener_libros(self) -> List[Dict]:
        """Obtiene todos los libros de KeyDB"""
        try:
            libros = []
            # Usar SCAN para encontrar todas las claves de libros
            for key in self.redis.scan_iter("libro:*"):
                libro_data = self.redis.get(key)
                if libro_data:
                    libros.append(json.loads(libro_data))
            # Ordenar por título
            return sorted(libros, key=lambda x: x["titulo"])
        except RedisError as e:
            print(f"{Fore.RED}Error al obtener libros: {e}")
            raise

    def buscar_libros(self, criterios: Dict) -> List[Dict]:
        """Busca libros según los criterios proporcionados"""
        try:
            resultados = []
            for key in self.redis.scan_iter("libro:*"):
                libro_data = self.redis.get(key)
                if libro_data:
                    libro = json.loads(libro_data)
                    coincide = True
                    
                    if 'titulo' in criterios and criterios['titulo'].lower() not in libro['titulo'].lower():
                        coincide = False
                    if 'autor' in criterios and criterios['autor'].lower() not in libro['autor'].lower():
                        coincide = False
                    if 'genero' in criterios and (not libro.get('genero') or criterios['genero'].lower() not in libro['genero'].lower()):
                        coincide = False
                    
                    if coincide:
                        resultados.append(libro)
            
            return sorted(resultados, key=lambda x: x["titulo"])
        except RedisError as e:
            print(f"{Fore.RED}Error al buscar libros: {e}")
            raise

    def obtener_libro_por_id(self, libro_id: str) -> Optional[Dict]:
        """Obtiene un libro específico por su ID"""
        try:
            libro_data = self.redis.get(f"libro:{libro_id}")
            return json.loads(libro_data) if libro_data else None
        except RedisError as e:
            print(f"{Fore.RED}Error al obtener libro: {e}")
            raise

    def actualizar_libro(self, libro_id: str, datos: Dict) -> bool:
        """Actualiza un libro existente"""
        try:
            libro = self.obtener_libro_por_id(libro_id)
            if not libro:
                return False
                
            # Actualizar campos
            libro.update(datos)
            self.redis.set(f"libro:{libro_id}", json.dumps(libro))
            return True
        except RedisError as e:
            print(f"{Fore.RED}Error al actualizar libro: {e}")
            raise

    def eliminar_libro(self, libro_id: str) -> bool:
        """Elimina un libro de KeyDB"""
        try:
            return self.redis.delete(f"libro:{libro_id}") > 0
        except RedisError as e:
            print(f"{Fore.RED}Error al eliminar libro: {e}")
            raise

def mostrar_menu():
    """Muestra el menú principal de la aplicación"""
    print(f"\n{Fore.CYAN}{Style.BRIGHT}===== BIBLIOTECA PERSONAL (KeyDB) ====={Style.RESET_ALL}")
    print(f"{Fore.GREEN}1. Agregar nuevo libro")
    print(f"{Fore.GREEN}2. Ver todos los libros")
    print(f"{Fore.GREEN}3. Buscar libros")
    print(f"{Fore.GREEN}4. Actualizar información de libro")
    print(f"{Fore.GREEN}5. Eliminar libro")
    print(f"{Fore.GREEN}6. Salir")

def mostrar_libros(libros: List[Dict]):
    """Muestra una lista de libros en formato tabular"""
    if not libros:
        print(f"{Fore.YELLOW}No se encontraron libros.")
        return

    # Preparar datos para la tabla
    tabla = []
    for libro in libros:
        tabla.append([
            libro["id"],
            libro["titulo"][:30] + "..." if len(libro["titulo"]) > 30 else libro["titulo"],
            libro["autor"][:20] + "..." if len(libro["autor"]) > 20 else libro["autor"],
            libro.get("genero", "N/A")[:15] + "..." if len(libro.get("genero", "")) > 15 else libro.get("genero", "N/A"),
            libro["estado"]
        ])

    # Mostrar tabla
    headers = ["ID", "Título", "Autor", "Género", "Estado"]
    print(tabulate(tabla, headers=headers, tablefmt="pretty"))

def validar_entrada(mensaje: str, obligatorio: bool = True, regex: str = None) -> str:
    """Valida la entrada del usuario"""
    while True:
        valor = input(mensaje).strip()
        
        if not valor and obligatorio:
            print(f"{Fore.RED}Este campo es obligatorio.")
            continue
            
        if regex and not re.match(regex, valor):
            print(f"{Fore.RED}Formato inválido.")
            continue
            
        return valor

def main():
    try:
        # Inicializar conexión con KeyDB
        biblioteca = BibliotecaKeyDB()

        while True:
            mostrar_menu()
            opcion = input(f"{Fore.YELLOW}Seleccione una opción (1-6): ")

            if opcion == "1":  # Agregar libro
                print(f"\n{Fore.CYAN}--- Agregar Nuevo Libro ---")
                
                titulo = validar_entrada(f"{Fore.YELLOW}Título: ")
                autor = validar_entrada(f"{Fore.YELLOW}Autor: ")
                genero = validar_entrada(f"{Fore.YELLOW}Género (opcional): ", obligatorio=False)
                
                print(f"\n{Fore.CYAN}Estado de lectura:")
                print(f"{Fore.GREEN}1. No leído")
                print(f"{Fore.GREEN}2. Leyendo")
                print(f"{Fore.GREEN}3. Leído")
                
                estado_opcion = validar_entrada(
                    f"{Fore.YELLOW}Seleccione estado (1-3): ",
                    regex=r"^[1-3]$"
                )
                
                estados = {
                    "1": "No leído",
                    "2": "Leyendo",
                    "3": "Leído"
                }
                estado = estados[estado_opcion]
                
                libro = biblioteca.agregar_libro(titulo, autor, genero, estado)
                print(f"\n{Fore.GREEN}Libro agregado con éxito. ID: {libro['id']}")

            elif opcion == "2":  # Listar libros
                print(f"\n{Fore.CYAN}--- Todos los Libros ---")
                libros = biblioteca.obtener_libros()
                mostrar_libros(libros)

            elif opcion == "3":  # Buscar libros
                print(f"\n{Fore.CYAN}--- Buscar Libros ---")
                print(f"{Fore.YELLOW}Ingrese términos de búsqueda (deje vacío para omitir)")
                
                titulo = input("Título: ")
                autor = input("Autor: ")
                genero = input("Género: ")
                
                criterios = {}
                if titulo: criterios["titulo"] = titulo
                if autor: criterios["autor"] = autor
                if genero: criterios["genero"] = genero
                
                libros = biblioteca.buscar_libros(criterios)
                mostrar_libros(libros)

            elif opcion == "4":  # Actualizar libro
                print(f"\n{Fore.CYAN}--- Actualizar Libro ---")
                libro_id = validar_entrada(f"{Fore.YELLOW}ID del libro a actualizar: ")
                
                libro = biblioteca.obtener_libro_por_id(libro_id)
                if not libro:
                    print(f"{Fore.RED}No se encontró un libro con ese ID.")
                    continue
                    
                print(f"\n{Fore.CYAN}Actualizando libro: {Fore.WHITE}{libro['titulo']}")
                print(f"{Fore.YELLOW}Deje vacío para mantener el valor actual")
                
                datos = {}
                nuevo_titulo = input(f"Título [{libro['titulo']}]: ")
                if nuevo_titulo: datos["titulo"] = nuevo_titulo
                
                nuevo_autor = input(f"Autor [{libro['autor']}]: ")
                if nuevo_autor: datos["autor"] = nuevo_autor
                
                nuevo_genero = input(f"Género [{libro.get('genero', 'N/A')}]: ")
                if nuevo_genero: datos["genero"] = nuevo_genero
                
                print(f"\n{Fore.CYAN}Estado actual: {Fore.WHITE}{libro['estado']}")
                print(f"{Fore.GREEN}1. No leído")
                print(f"{Fore.GREEN}2. Leyendo")
                print(f"{Fore.GREEN}3. Leído")
                print(f"{Fore.GREEN}4. Mantener actual")
                
                estado_opcion = validar_entrada(
                    f"{Fore.YELLOW}Seleccione nuevo estado (1-4): ",
                    regex=r"^[1-4]$"
                )
                
                if estado_opcion in ["1", "2", "3"]:
                    datos["estado"] = estados[estado_opcion]
                
                if datos:
                    actualizado = biblioteca.actualizar_libro(libro_id, datos)
                    if actualizado:
                        print(f"{Fore.GREEN}Libro actualizado con éxito.")
                    else:
                        print(f"{Fore.YELLOW}No se realizaron cambios.")
                else:
                    print(f"{Fore.YELLOW}No se proporcionaron cambios.")

            elif opcion == "5":  # Eliminar libro
                print(f"\n{Fore.CYAN}--- Eliminar Libro ---")
                libro_id = validar_entrada(f"{Fore.YELLOW}ID del libro a eliminar: ")
                
                libro = biblioteca.obtener_libro_por_id(libro_id)
                if not libro:
                    print(f"{Fore.RED}No se encontró un libro con ese ID.")
                    continue
                    
                confirmacion = input(f"{Fore.RED}¿Eliminar '{libro['titulo']}'? (s/n): ").lower()
                if confirmacion == "s":
                    eliminado = biblioteca.eliminar_libro(libro_id)
                    if eliminado:
                        print(f"{Fore.GREEN}Libro eliminado con éxito.")
                    else:
                        print(f"{Fore.RED}No se pudo eliminar el libro.")
                else:
                    print(f"{Fore.YELLOW}Operación cancelada.")

            elif opcion == "6":  # Salir
                print(f"{Fore.CYAN}Saliendo del programa...")
                break

            else:
                print(f"{Fore.RED}Opción inválida. Intente nuevamente.")

    except Exception as e:
        print(f"{Fore.RED}Error inesperado: {e}")
    finally:
        if 'biblioteca' in locals():
            biblioteca.redis.close()
        print(f"{Fore.CYAN}Programa finalizado.")

if __name__ == "__main__":
    import re
    main()