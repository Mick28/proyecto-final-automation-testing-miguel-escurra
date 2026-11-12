"""Pruebas de API sobre el recurso /posts de JSONPlaceholder.

Cubre los métodos GET, POST, PUT y DELETE y valida, en cada caso,
código de estado, estructura (JSON Schema) y contenido de la respuesta.
Nota: JSONPlaceholder es una API simulada: responde como si creara,
modificara o borrara recursos, pero no guarda los cambios.
"""
import pytest
from jsonschema import validate

from utils import config
from utils.data_loader import read_json
from utils.schemas import POST_LIST_SCHEMA, POST_SCHEMA

# Reintenta hasta 2 veces ante fallos de red (servicio externo), según lo visto en la Clase 13
pytestmark = [pytest.mark.api, pytest.mark.flaky(reruns=2, reruns_delay=2)]

NEW_POSTS = [pytest.param(post, id=post["caso"]) for post in read_json("api_posts.json")]


@pytest.mark.smoke
def test_obtener_post_existente(api_client):
    """TC-API-01: GET /posts/1 devuelve 200, estructura válida y el post pedido."""
    response = api_client.get("/posts/1")

    assert response.status_code == 200
    assert response.headers["Content-Type"].startswith("application/json")
    assert response.elapsed.total_seconds() < config.API_MAX_RESPONSE_TIME
    post = response.json()
    validate(instance=post, schema=POST_SCHEMA)
    assert post["id"] == 1
    assert post["userId"] == 1
    assert post["title"].strip() != ""


def test_listar_posts_filtrados_por_usuario(api_client):
    """TC-API-02: GET /posts?userId=2 devuelve solo los posts de ese usuario."""
    response = api_client.get("/posts", params={"userId": 2})

    assert response.status_code == 200
    posts = response.json()
    validate(instance=posts, schema=POST_LIST_SCHEMA)
    assert len(posts) == 10
    assert {post["userId"] for post in posts} == {2}


@pytest.mark.negative
@pytest.mark.parametrize("post_id", [0, 101, 99999], ids=lambda value: f"id_{value}")
def test_obtener_post_inexistente_devuelve_404(api_client, post_id):
    """TC-API-03: pedir un post que no existe responde 404 con un cuerpo vacío."""
    response = api_client.get(f"/posts/{post_id}")

    assert response.status_code == 404
    assert response.json() == {}


@pytest.mark.smoke
@pytest.mark.parametrize("new_post", NEW_POSTS)
def test_crear_post(api_client, new_post):
    """TC-API-04: POST /posts responde 201 y devuelve los datos enviados con un id nuevo."""
    payload = {key: new_post[key] for key in ("title", "body", "userId")}

    response = api_client.post("/posts", json=payload)

    assert response.status_code == 201
    created = response.json()
    validate(instance=created, schema=POST_SCHEMA)
    assert created["id"] == 101  # JSONPlaceholder siempre asigna el id 101
    for key, value in payload.items():
        assert created[key] == value, f"El campo '{key}' no coincide"


def test_actualizar_post(api_client):
    """TC-API-05: PUT /posts/1 reemplaza el recurso y devuelve los datos actualizados."""
    payload = {"id": 1, "title": "Título actualizado", "body": "Cuerpo actualizado", "userId": 1}

    response = api_client.put("/posts/1", json=payload)

    assert response.status_code == 200
    updated = response.json()
    validate(instance=updated, schema=POST_SCHEMA)
    assert updated == payload


def test_eliminar_post(api_client):
    """TC-API-06: DELETE /posts/1 responde 200 con un cuerpo vacío."""
    response = api_client.delete("/posts/1")

    assert response.status_code == 200
    assert response.json() == {}
