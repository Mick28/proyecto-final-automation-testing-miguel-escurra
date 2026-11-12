"""Fixtures exclusivas de las pruebas de API."""
import pytest

from utils.api_client import ApiClient


@pytest.fixture(scope="session")
def api_client():
    """Un único cliente HTTP (con su sesión) para toda la suite de API."""
    client = ApiClient()
    yield client
    client.close()
