from datetime import datetime
from db import db

class Book(db.Model):
    __tablename__ = "books"

    id = db.Column(db.String(36), primary_key=True)  # UUID en texto
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(120), nullable=False)
    genre = db.Column(db.String(80), nullable=True)
    status = db.Column(db.String(30), nullable=False, default="No leído")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
