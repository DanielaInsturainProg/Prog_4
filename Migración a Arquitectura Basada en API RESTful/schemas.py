from marshmallow import Schema, fields, ValidationError

def validate_status(value):
    if value not in ["No leído", "Leyendo", "Leído"]:
        raise ValidationError("status inválido. Usa: No leído | Leyendo | Leído")

class BookSchema(Schema):
    id = fields.Str(dump_only=True)
    title = fields.Str(required=True)
    author = fields.Str(required=True)
    genre = fields.Str(allow_none=True)
    status = fields.Str(load_default="No leído", validate=validate_status)
    created_at = fields.DateTime(dump_only=True)

book_schema = BookSchema()
books_schema = BookSchema(many=True)
