"""Cliente HTTP reutilizable para las pruebas de API.

Envuelve requests.Session para:
- armar las URLs a partir de una URL base,
- aplicar un timeout a todas las peticiones,
- registrar en el log cada petición y su respuesta (método, URL, status, tiempo).
"""
import requests

from utils import config
from utils.logger import get_logger


class ApiClient:
    def __init__(self, base_url: str = config.API_BASE_URL, timeout: int = config.API_TIMEOUT):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({"Content-type": "application/json; charset=UTF-8"})
        self.logger = get_logger("api.client")

    def request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        url = f"{self.base_url}{endpoint}"
        self.logger.info("→ %s %s %s", method, url, self._describe_payload(kwargs))
        response = self.session.request(method, url, timeout=self.timeout, **kwargs)
        self.logger.info("← %s %s | status %s | %.0f ms",
                         method, url, response.status_code, response.elapsed.total_seconds() * 1000)
        return response

    def get(self, endpoint: str, **kwargs) -> requests.Response:
        return self.request("GET", endpoint, **kwargs)

    def post(self, endpoint: str, **kwargs) -> requests.Response:
        return self.request("POST", endpoint, **kwargs)

    def put(self, endpoint: str, **kwargs) -> requests.Response:
        return self.request("PUT", endpoint, **kwargs)

    def delete(self, endpoint: str, **kwargs) -> requests.Response:
        return self.request("DELETE", endpoint, **kwargs)

    def close(self):
        self.session.close()

    @staticmethod
    def _describe_payload(kwargs: dict) -> str:
        if "json" in kwargs:
            return f"| body: {kwargs['json']}"
        if "params" in kwargs:
            return f"| params: {kwargs['params']}"
        return ""
