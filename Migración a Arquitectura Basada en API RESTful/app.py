import os, uuid
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from db import db
from models import Book
from schemas import book_schema, books_schema

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///books.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    with app.app_context():
        db.create_all()

    @app.get("/health")
    def health():
        return {"status": "ok"}, 200

    # GET /books
    @app.get("/books")
    def list_books():
        books = Book.query.order_by(Book.title.asc()).all()
        return jsonify(books_schema.dump(books)), 200

    # GET /books/<id>
    @app.get("/books/<string:book_id>")
    def get_book(book_id):
        book = Book.query.get(book_id)
        if not book:
            return {"error": "book not found"}, 404
        return book_schema.dump(book), 200

    # POST /books
    @app.post("/books")
    def create_book():
        json_data = request.get_json(silent=True) or {}
        try:
            data = book_schema.load(json_data)
        except Exception as e:
            return {"error": str(e)}, 400

        new_book = Book(
            id=str(uuid.uuid4()),
            title=data["title"].strip(),
            author=data["author"].strip(),
            genre=(data.get("genre") or "").strip() or None,
            status=data.get("status", "No leído"),
        )
        db.session.add(new_book)
        db.session.commit()
        return book_schema.dump(new_book), 201

    # PUT /books/<id>
    @app.put("/books/<string:book_id>")
    def update_book(book_id):
        book = Book.query.get(book_id)
        if not book:
            return {"error": "book not found"}, 404

        json_data = request.get_json(silent=True) or {}
        # Cargar con partición de validación (aceptar campos parciales)
        for key in ["title", "author", "genre", "status"]:
            if key in json_data:
                setattr(book, key, json_data[key])
        try:
            # Validar con schema (copia temporal)
            _ = book_schema.load({
                "title": book.title,
                "author": book.author,
                "genre": book.genre,
                "status": book.status,
            })
        except Exception as e:
            return {"error": str(e)}, 400

        db.session.commit()
        return book_schema.dump(book), 200

    # DELETE /books/<id>
    @app.delete("/books/<string:book_id>")
    def delete_book(book_id):
        book = Book.query.get(book_id)
        if not book:
            return {"error": "book not found"}, 404
        db.session.delete(book)
        db.session.commit()
        return {"message": "deleted"}, 200

    # Manejo global de errores
    @app.errorhandler(500)
    def internal_err(e):
        return {"error": "internal server error"}, 500

    return app

app = create_app()

if __name__ == "__main__":
    app.run(host=os.getenv("API_HOST", "0.0.0.0"),
            port=int(os.getenv("API_PORT", "5001")))
