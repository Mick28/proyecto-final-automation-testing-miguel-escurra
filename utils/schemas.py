"""Esquemas JSON (formato JSON Schema) de las respuestas de JSONPlaceholder.

Se usan con jsonschema.validate() para verificar la ESTRUCTURA de cada
respuesta: qué campos tiene que traer y de qué tipo es cada uno.
"""

POST_SCHEMA = {
    "type": "object",
    "required": ["userId", "id", "title", "body"],
    "properties": {
        "userId": {"type": "integer"},
        "id": {"type": "integer"},
        "title": {"type": "string"},
        "body": {"type": "string"},
    },
}

POST_LIST_SCHEMA = {"type": "array", "items": POST_SCHEMA}

COMMENT_SCHEMA = {
    "type": "object",
    "required": ["postId", "id", "name", "email", "body"],
    "properties": {
        "postId": {"type": "integer"},
        "id": {"type": "integer"},
        "name": {"type": "string"},
        "email": {"type": "string", "pattern": "^[^@\\s]+@[^@\\s]+$"},
        "body": {"type": "string"},
    },
}

COMMENT_LIST_SCHEMA = {"type": "array", "minItems": 1, "items": COMMENT_SCHEMA}

USER_SCHEMA = {
    "type": "object",
    "required": ["id", "name", "username", "email", "address", "company"],
    "properties": {
        "id": {"type": "integer"},
        "name": {"type": "string"},
        "username": {"type": "string"},
        "email": {"type": "string"},
        "address": {
            "type": "object",
            "required": ["street", "city", "zipcode"],
        },
        "company": {"type": "object", "required": ["name"]},
    },
}
