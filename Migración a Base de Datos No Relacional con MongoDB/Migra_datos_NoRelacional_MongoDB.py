import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, PyMongoError
from colorama import init, Fore, Style
from tabulate import tabulate
from dotenv import load_dotenv
from bson import ObjectId
from typing import List, Dict, Optional

# Inicializar colorama
init(autoreset=True)

# Cargar variables de entorno
load_dotenv()

class BibliotecaMongoDB:
    """Clase para manejar las operaciones con MongoDB"""
    
    def __init__(self):
        """Inicializa la conexión con MongoDB"""
        try:
            # Conexión a MongoDB (usando variables de entorno)
            self.client = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017/"))
            self.db = self.client["biblioteca"]
            self.libros = self.db["libros"]
            
            # Verificar conexión
            self.client.admin.command('ping')
            print(f"{Fore.GREEN}Conexión exitosa a MongoDB")
        except ConnectionFailure as e:
            print(f"{Fore.RED}Error al conectar a MongoDB: {e}")
            raise

    def agregar_libro(self, titulo: str, autor: str, genero: str, estado: str) -> Dict:
        """Agrega un nuevo libro a la colección"""
        libro = {
            "titulo": titulo,
            "autor": autor,
            "genero": genero,
            "estado": estado,
            "fecha_creacion": datetime.datetime.now()
        }
        
        try:
            result = self.libros.insert_one(libro)
            libro["_id"] = result.inserted_id
            return libro
        except PyMongoError as e:
            print(f"{Fore.RED}Error al agregar libro: {e}")
            raise

    def obtener_libros(self) -> List[Dict]:
        """Obtiene todos los libros de la colección"""
        try:
            return list(self.libros.find().sort("titulo"))
        except PyMongoError as e:
            print(f"{Fore.RED}Error al obtener libros: {e}")
            raise

    def buscar_libros(self, criterios: Dict) -> List[Dict]:
        """Busca libros según los criterios proporcionados"""
        try:
            query = {}
            
            if 'titulo' in criterios:
                query['titulo'] = {"$regex": criterios['titulo'], "$options": "i"}
            if 'autor' in criterios:
                query['autor'] = {"$regex": criterios['autor'], "$options": "i"}
            if 'genero' in criterios:
                query['genero'] = {"$regex": criterios['genero'], "$options": "i"}
            
            return list(self.libros.find(query).sort("titulo"))
        except PyMongoError as e:
            print(f"{Fore.RED}Error al buscar libros: {e}")
            raise

    def actualizar_libro(self, libro_id: str, datos: Dict) -> bool:
        """Actualiza un libro existente"""
        try:
            if not datos:
                return False
                
            result = self.libros.update_one(
                {"_id": ObjectId(libro_id)},
                {"$set": datos}
            )
            return result.modified_count > 0
        except PyMongoError as e:
            print(f"{Fore.RED}Error al actualizar libro: {e}")
            raise

    def eliminar_libro(self, libro_id: str) -> bool:
        """Elimina un libro de la colección"""
        try:
            result = self.libros.delete_one({"_id": ObjectId(libro_id)})
            return result.deleted_count > 0
        except PyMongoError as e:
            print(f"{Fore.RED}Error al eliminar libro: {e}")
            raise

def mostrar_menu():
    """Muestra el menú principal de la aplicación"""
    print(f"\n{Fore.CYAN}{Style.BRIGHT}===== BIBLIOTECA PERSONAL (MongoDB) ====={Style.RESET_ALL}")
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
            str(libro["_id"]),
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
        # Inicializar conexión con MongoDB
        biblioteca = BibliotecaMongoDB()

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
                print(f"\n{Fore.GREEN}Libro agregado con éxito. ID: {libro['_id']}")

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
                
                try:
                    libro = biblioteca.libros.find_one({"_id": ObjectId(libro_id)})
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
                        
                except Exception as e:
                    print(f"{Fore.RED}Error: {e}")

            elif opcion == "5":  # Eliminar libro
                print(f"\n{Fore.CYAN}--- Eliminar Libro ---")
                libro_id = validar_entrada(f"{Fore.YELLOW}ID del libro a eliminar: ")
                
                try:
                    libro = biblioteca.libros.find_one({"_id": ObjectId(libro_id)})
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
                        
                except Exception as e:
                    print(f"{Fore.RED}Error: {e}")

            elif opcion == "6":  # Salir
                print(f"{Fore.CYAN}Saliendo del programa...")
                break

            else:
                print(f"{Fore.RED}Opción inválida. Intente nuevamente.")

    except Exception as e:
        print(f"{Fore.RED}Error inesperado: {e}")
    finally:
        if 'biblioteca' in locals():
            biblioteca.client.close()
        print(f"{Fore.CYAN}Programa finalizado.")

if __name__ == "__main__":
    import re
    import datetime
    main()