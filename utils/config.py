"""Configuración central del framework.

Todos los valores pueden sobrescribirse con variables de entorno, lo que
permite correr la misma suite en local, en CI o contra otro entorno sin
tocar el código.
"""
import os
from pathlib import Path

# Rutas del proyecto (pathlib evita problemas de "/" vs "\" entre Windows y Linux)
ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "datos"
REPORTS_DIR = ROOT_DIR / "reports"
SCREENSHOTS_DIR = REPORTS_DIR / "screenshots"
LOGS_DIR = ROOT_DIR / "logs"

# Aplicaciones bajo prueba
BASE_URL = os.getenv("BASE_URL", "https://www.saucedemo.com").rstrip("/")
API_BASE_URL = os.getenv("API_BASE_URL", "https://jsonplaceholder.typicode.com").rstrip("/")

# Navegador
HEADLESS = os.getenv("HEADLESS", "false").lower() in ("1", "true", "yes")
CHROMEDRIVER_PATH = os.getenv("CHROMEDRIVER_PATH")  # opcional; si no está, Selenium Manager lo resuelve
EXPLICIT_WAIT = int(os.getenv("EXPLICIT_WAIT", "10"))

# API
API_TIMEOUT = int(os.getenv("API_TIMEOUT", "10"))
API_MAX_RESPONSE_TIME = float(os.getenv("API_MAX_RESPONSE_TIME", "5"))

# Usuario por defecto para los flujos que necesitan estar logueados
STANDARD_USER = os.getenv("SAUCE_USER", "standard_user")
STANDARD_PASSWORD = os.getenv("SAUCE_PASSWORD", "secret_sauce")
