"""Logger centralizado del framework.

- Escribe en logs/suite.log con rotación automática (1 MB x 5 archivos).
- Nivel INFO o superior, con fecha y hora en cada línea.
- Los mensajes también se propagan a pytest, que los adjunta en el
  reporte HTML dentro de la sección "Captured log" de cada test.

Uso:
    from utils.logger import get_logger
    logger = get_logger(__name__)
    logger.info("Iniciando login con usuario: %s", usuario)
"""
import logging
from logging.handlers import RotatingFileHandler

from utils.config import LOGS_DIR

ROOT_LOGGER_NAME = "qa"
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def _configure_root_logger() -> logging.Logger:
    """Configura una única vez el logger raíz del framework."""
    root = logging.getLogger(ROOT_LOGGER_NAME)
    if root.handlers:  # ya configurado: evita duplicar líneas en el archivo
        return root

    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    file_handler = RotatingFileHandler(
        LOGS_DIR / "suite.log",
        maxBytes=1024 * 1024,  # 1 MB por archivo
        backupCount=5,         # se conservan 5 archivos históricos
        encoding="utf-8",
    )
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))

    root.setLevel(logging.INFO)
    root.addHandler(file_handler)
    root.propagate = True  # permite que pytest capture los logs para el reporte
    return root


def get_logger(name: str) -> logging.Logger:
    """Devuelve un logger hijo (por ejemplo 'qa.pages.login_page')."""
    _configure_root_logger()
    return logging.getLogger(f"{ROOT_LOGGER_NAME}.{name}")
