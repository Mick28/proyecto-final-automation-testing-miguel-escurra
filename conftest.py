"""Configuración global de pytest: fixtures compartidas y hooks de reporte.

Contiene:
- Opción --headless para correr el navegador sin interfaz.
- Fixtures de UI (driver, login_page, inventory_page): un navegador nuevo
  por test, así un fallo nunca contamina al siguiente.
- Hook que guarda un screenshot cuando un test de UI falla y lo adjunta
  al reporte HTML.
- Personalización del reporte HTML (título, metadatos, columnas extra).
- Registro en el log del inicio, fin y resultado de cada test.
"""
import base64
import html
import re
from datetime import datetime

import pytest
from pytest_metadata.plugin import metadata_key

from pages.inventory_page import InventoryPage
from pages.login_page import LoginPage
from utils import config as settings
from utils.driver_factory import create_chrome_driver
from utils.logger import get_logger

logger = get_logger("conftest")


# ---------------------------------------------------------------------------
# Opciones de línea de comandos y configuración inicial
# ---------------------------------------------------------------------------
def pytest_addoption(parser):
    parser.addoption(
        "--headless", action="store_true", default=False,
        help="Ejecuta Chrome sin interfaz gráfica (también se puede usar HEADLESS=true)",
    )


def pytest_configure(config):
    settings.SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    # Metadatos que aparecen en la sección "Environment" del reporte HTML
    metadata = config.stash[metadata_key]
    metadata["Proyecto"] = "Proyecto Final – Framework de Automatización de Pruebas"
    metadata["Autor"] = "Miguel Angel Escurra"
    metadata["Sitio UI"] = settings.BASE_URL
    metadata["API"] = settings.API_BASE_URL
    metadata["Navegador"] = "Chrome (headless)" if _is_headless(config) else "Chrome"
    logger.info("===== Inicio de la ejecución de la suite =====")


def pytest_unconfigure(config):
    logger.info("===== Fin de la ejecución de la suite =====")


def _is_headless(config) -> bool:
    return config.getoption("--headless") or settings.HEADLESS


# ---------------------------------------------------------------------------
# Fixtures de UI
# ---------------------------------------------------------------------------
@pytest.fixture
def driver(request):
    """Abre un Chrome nuevo para cada test y lo cierra al terminar (teardown)."""
    browser = create_chrome_driver(headless=_is_headless(request.config))
    yield browser
    browser.quit()
    logger.info("Chrome cerrado")


@pytest.fixture
def login_page(driver):
    """Pantalla de login ya abierta."""
    return LoginPage(driver).open()


@pytest.fixture
def inventory_page(driver):
    """Catálogo con el usuario estándar ya logueado (precondición de varios tests)."""
    LoginPage(driver).open().login(settings.STANDARD_USER, settings.STANDARD_PASSWORD)
    return InventoryPage(driver).wait_until_loaded()


@pytest.fixture(autouse=True)
def log_test_lifecycle(request):
    """Deja en el log una marca de inicio y fin de cada test."""
    logger.info("▶ INICIO  %s", request.node.nodeid)
    yield
    logger.info("■ FIN     %s", request.node.nodeid)


# ---------------------------------------------------------------------------
# Screenshots automáticos ante fallos + datos extra para el reporte
# ---------------------------------------------------------------------------
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    driver = getattr(item, "funcargs", {}).get("driver")

    # Tipo de test para la columna "Tipo" del reporte
    report.test_type = "UI" if "ui" in item.keywords else "API" if "api" in item.keywords else "-"

    # URL en la que estaba el navegador (columna "URL" del reporte)
    if driver and report.when in ("setup", "call"):
        try:
            report.page_url = driver.current_url
        except Exception:  # el navegador pudo haberse cerrado
            report.page_url = "-"

    if report.when == "call" or (report.when == "setup" and report.failed):
        log = logger.info if report.passed else logger.error
        log("Resultado %s -> %s (%.2f s)", item.nodeid, report.outcome.upper(), report.duration)

    if report.failed and report.when in ("setup", "call") and driver:
        _attach_screenshot(item, report, driver)


def _attach_screenshot(item, report, driver):
    """Guarda la captura en reports/screenshots/ y la incrusta en el reporte HTML."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_test_name = re.sub(r"[^\w\-]", "_", item.name).strip("_")
    file_path = settings.SCREENSHOTS_DIR / f"{safe_test_name}_{timestamp}.png"
    try:
        png_bytes = driver.get_screenshot_as_png()
    except Exception as error:
        logger.error("No se pudo tomar el screenshot de %s: %s", item.nodeid, error)
        return

    file_path.write_bytes(png_bytes)
    logger.error("Screenshot del fallo guardado en %s", file_path.relative_to(settings.ROOT_DIR))

    pytest_html = item.config.pluginmanager.getplugin("html")
    if pytest_html:
        extras = getattr(report, "extras", [])
        extras.append(pytest_html.extras.image(base64.b64encode(png_bytes).decode(),
                                               name=file_path.name))
        report.extras = extras


# ---------------------------------------------------------------------------
# Personalización del reporte HTML (pytest-html 4.x)
# ---------------------------------------------------------------------------
def pytest_html_report_title(report):
    report.title = "Proyecto Final Automation Testing – Miguel Angel Escurra"


def pytest_html_results_table_header(cells):
    cells.insert(2, "<th>Tipo</th>")
    cells.insert(3, "<th>URL</th>")


def pytest_html_results_table_row(report, cells):
    cells.insert(2, f"<td>{getattr(report, 'test_type', '-')}</td>")
    cells.insert(3, f"<td>{html.escape(getattr(report, 'page_url', '-'))}</td>")
