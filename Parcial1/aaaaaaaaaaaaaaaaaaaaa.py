import json
import os
from tabulate import tabulate

# Archivo donde se guardarán los artículos
DATA_FILE = "data.json"


# ----------------- Funciones auxiliares -----------------
def cargar_datos():
    """Carga los artículos desde el archivo JSON."""
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def guardar_datos(articulos):
    """Guarda los artículos en el archivo JSON."""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(articulos, f, indent=4, ensure_ascii=False)


def generar_id(articulos):
    """Genera un ID único incremental para cada artículo."""
    if not articulos:
        return 1
    return max(item["id"] for item in articulos) + 1


# ----------------- Funciones CRUD -----------------
def registrar_articulo():
    articulos = cargar_datos()
    nuevo = {
        "id": generar_id(articulos),
        "nombre": input("Nombre: ").strip(),
        "categoria": input("Categoría: ").strip(),
        "cantidad": int(input("Cantidad: ")),
        "precio_unitario": float(input("Precio unitario: ")),
        "descripcion": input("Descripción: ").strip(),
    }
    articulos.append(nuevo)
    guardar_datos(articulos)
    print("✅ Artículo registrado con éxito.")


def listar_articulos():
    articulos = cargar_datos()
    if not articulos:
        print("⚠️ No hay artículos registrados.")
        return
    tabla = [[a["id"], a["nombre"], a["categoria"], a["cantidad"], a["precio_unitario"], a["descripcion"]] for a in articulos]
    print(tabulate(tabla, headers=["ID", "Nombre", "Categoría", "Cantidad", "Precio Unitario", "Descripción"], tablefmt="grid"))


def buscar_articulos():
    articulos = cargar_datos()
    criterio = input("Buscar por (nombre/categoría): ").strip().lower()
    valor = input(f"Ingrese el {criterio}: ").strip().lower()

    encontrados = [a for a in articulos if valor in a[criterio].lower()]

    if encontrados:
        tabla = [[a["id"], a["nombre"], a["categoria"], a["cantidad"], a["precio_unitario"], a["descripcion"]] for a in encontrados]
        print(tabulate(tabla, headers=["ID", "Nombre", "Categoría", "Cantidad", "Precio Unitario", "Descripción"], tablefmt="grid"))
    else:
        print("⚠️ No se encontraron coincidencias.")


def editar_articulo():
    articulos = cargar_datos()
    listar_articulos()
    try:
        art_id = int(input("Ingrese el ID del artículo a editar: "))
    except ValueError:
        print("⚠️ ID inválido.")
        return

    articulo = next((a for a in articulos if a["id"] == art_id), None)
    if not articulo:
        print("⚠️ Artículo no encontrado.")
        return

    print("Deje en blanco si no desea modificar un campo.")
    nuevo_nombre = input(f"Nombre ({articulo['nombre']}): ").strip()
    nueva_categoria = input(f"Categoría ({articulo['categoria']}): ").strip()
    nueva_cantidad = input(f"Cantidad ({articulo['cantidad']}): ").strip()
    nuevo_precio = input(f"Precio unitario ({articulo['precio_unitario']}): ").strip()
    nueva_desc = input(f"Descripción ({articulo['descripcion']}): ").strip()

    if nuevo_nombre:
        articulo["nombre"] = nuevo_nombre
    if nueva_categoria:
        articulo["categoria"] = nueva_categoria
    if nueva_cantidad:
        articulo["cantidad"] = int(nueva_cantidad)
    if nuevo_precio:
        articulo["precio_unitario"] = float(nuevo_precio)
    if nueva_desc:
        articulo["descripcion"] = nueva_desc

    guardar_datos(articulos)
    print("✅ Artículo actualizado.")


def eliminar_articulo():
    articulos = cargar_datos()
    listar_articulos()
    try:
        art_id = int(input("Ingrese el ID del artículo a eliminar: "))
    except ValueError:
        print("⚠️ ID inválido.")
        return

    articulos = [a for a in articulos if a["id"] != art_id]
    guardar_datos(articulos)
    print("✅ Artículo eliminado.")


# ----------------- Menú principal -----------------
def menu():
    while True:
        print("\n📌 Sistema de Presupuesto")
        print("1. Registrar artículo")
        print("2. Listar artículos")
        print("3. Buscar artículos")
        print("4. Editar artículo")
        print("5. Eliminar artículo")
        print("6. Salir")

        opcion = input("Seleccione una opción: ").strip()

        if opcion == "1":
            registrar_articulo()
        elif opcion == "2":
            listar_articulos()
        elif opcion == "3":
            buscar_articulos()
        elif opcion == "4":
            editar_articulo()
        elif opcion == "5":
            eliminar_articulo()
        elif opcion == "6":
            print("👋 Saliendo del sistema. ¡Hasta luego!")
            break
        else:
            print("⚠️ Opción no válida, intente de nuevo.")


if __name__ == "__main__":
    menu()
