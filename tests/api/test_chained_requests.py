"""Encadenamiento de peticiones: cada paso usa datos de la respuesta anterior."""
import pytest
from jsonschema import validate

from utils.schemas import COMMENT_LIST_SCHEMA, POST_SCHEMA, USER_SCHEMA

pytestmark = [pytest.mark.api, pytest.mark.flaky(reruns=2, reruns_delay=2)]


def test_crear_post_y_consultar_su_autor(api_client):
    """TC-API-07: POST crea un post -> con el userId devuelto se consulta GET /users/{id}."""
    # Paso 1: crear el recurso
    create_response = api_client.post("/posts", json={
        "title": "Post encadenado", "body": "Creado para obtener luego a su autor", "userId": 3,
    })
    assert create_response.status_code == 201
    created_post = create_response.json()
    validate(instance=created_post, schema=POST_SCHEMA)

    # Paso 2: usar el dato devuelto para la siguiente petición
    author_id = created_post["userId"]
    user_response = api_client.get(f"/users/{author_id}")

    assert user_response.status_code == 200
    author = user_response.json()
    validate(instance=author, schema=USER_SCHEMA)
    assert author["id"] == author_id


def test_obtener_post_y_sus_comentarios(api_client):
    """TC-API-08: GET /posts/1 -> con su id se piden sus comentarios y se verifica la relación."""
    post_response = api_client.get("/posts/1")
    assert post_response.status_code == 200
    post_id = post_response.json()["id"]

    comments_response = api_client.get(f"/posts/{post_id}/comments")

    assert comments_response.status_code == 200
    comments = comments_response.json()
    validate(instance=comments, schema=COMMENT_LIST_SCHEMA)
    assert all(comment["postId"] == post_id for comment in comments), \
        "Hay comentarios que no pertenecen al post consultado"
