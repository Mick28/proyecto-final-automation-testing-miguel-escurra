"""Test de demostración que FALLA A PROPÓSITO.

Sirve para mostrar en la presentación cómo el framework guarda el
screenshot del fallo y lo adjunta al reporte HTML. Por defecto se omite;
para ejecutarlo:

    DEMO_FALLO=1 pytest -m demo            (Linux / macOS)
    set DEMO_FALLO=1 && pytest -m demo     (Windows cmd)
"""
import os

import pytest

pytestmark = [
    pytest.mark.ui,
    pytest.mark.demo,
    pytest.mark.skipif(not os.getenv("DEMO_FALLO"), reason="Demo de fallo: activar con DEMO_FALLO=1"),
]


def test_demo_fallo_genera_screenshot(inventory_page):
    """Espera un título incorrecto para forzar el fallo y la captura."""
    assert inventory_page.get_page_title() == "Productos", "Fallo intencional para demostrar el screenshot"
