import os
from flask import Flask, render_template, request, redirect, url_for, flash
from dotenv import load_dotenv
from helpers import api_request, flash_api_error

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret-key-123")

@app.route("/")
def index():
    data, err, status = api_request("GET", "/books")
    if err:
        flash_api_error(err)
        data = []
    # Normaliza claves a dot-access en Jinja (simplemente pasamos dicts)
    return render_template("books_list.html", books=data)

@app.route("/books/add", methods=["GET", "POST"])
def add_book():
    if request.method == "POST":
        payload = {
            "title": request.form.get("title", "").strip(),
            "author": request.form.get("author", "").strip(),
            "genre": request.form.get("genre", "").strip() or None,
            "status": request.form.get("status", "No leído")
        }
        data, err, status = api_request("POST", "/books", json=payload)
        if err:
            flash_api_error(err, "No se pudo crear el libro")
            return redirect(url_for("add_book"))
        flash("Libro creado correctamente", "success")
        return redirect(url_for("index"))
    return render_template("book_form.html", book=None)

@app.route("/books/edit/<string:book_id>", methods=["GET", "POST"])
def edit_book(book_id):
    if request.method == "POST":
        payload = {
            "title": request.form.get("title", "").strip(),
            "author": request.form.get("author", "").strip(),
            "genre": request.form.get("genre", "").strip() or None,
            "status": request.form.get("status", "No leído")
        }
        _, err, _ = api_request("PUT", f"/books/{book_id}", json=payload)
        if err:
            flash_api_error(err, "No se pudo actualizar el libro")
            return redirect(url_for("edit_book", book_id=book_id))
        flash("Libro actualizado", "success")
        return redirect(url_for("index"))
    # GET para precargar el formulario
    data, err, status = api_request("GET", f"/books/{book_id}")
    if err:
        flash_api_error(err, "No se encontró el libro")
        return redirect(url_for("index"))
    return render_template("book_form.html", book=data)

@app.route("/books/delete/<string:book_id>", methods=["GET", "POST"])
def delete_book(book_id):
    if request.method == "POST":
        _, err, _ = api_request("DELETE", f"/books/{book_id}")
        if err:
            flash_api_error(err, "No se pudo eliminar el libro")
            return redirect(url_for("delete_book", book_id=book_id))
        flash("Libro eliminado", "success")
        return redirect(url_for("index"))
    # GET para confirmar
    data, err, _ = api_request("GET", f"/books/{book_id}")
    if err:
        flash_api_error(err, "No se encontró el libro")
        return redirect(url_for("index"))
    return render_template("book_confirm_delete.html", book=data)

if __name__ == "__main__":
    app.run(port=5000, debug=True)
