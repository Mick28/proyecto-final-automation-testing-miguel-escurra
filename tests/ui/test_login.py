"""Casos de prueba de autenticación en SauceDemo.

Los datos (usuarios, contraseñas y mensajes esperados) se leen de
datos/login_users.csv: para sumar un caso nuevo basta con agregar una fila.
"""
import pytest

from pages.inventory_page import InventoryPage
from pages.login_page import LoginPage
from utils.data_loader import read_csv

pytestmark = pytest.mark.ui

# Cada fila del CSV se convierte en un caso; las filas de error llevan el marker "negative"
LOGIN_CASES = [
    pytest.param(row, id=row["caso"],
                 marks=pytest.mark.negative if row["resultado_esperado"] == "error" else ())
    for row in read_csv("login_users.csv")
]


@pytest.mark.smoke
@pytest.mark.parametrize("login_case", LOGIN_CASES)
def test_login_con_distintas_credenciales(driver, login_page, login_case):
    """TC-UI-01: login exitoso con usuario válido y mensajes de error con credenciales inválidas."""
    login_page.login(login_case["username"], login_case["password"])

    if login_case["resultado_esperado"] == "exito":
        inventory = InventoryPage(driver).wait_until_loaded()
        assert "/inventory.html" in inventory.current_url
        assert inventory.get_page_title() == "Products"
    else:
        assert login_page.get_error_message() == login_case["mensaje_error"]
        assert "/inventory.html" not in driver.current_url, "No debería haber ingresado al catálogo"


def test_logout_vuelve_al_login(driver, inventory_page):
    """TC-UI-02: el usuario cierra sesión desde el menú lateral y vuelve al login."""
    inventory_page.logout()

    assert LoginPage(driver).is_displayed()
    assert "/inventory.html" not in driver.current_url


@pytest.mark.negative
def test_acceso_directo_al_catalogo_sin_login(driver):
    """TC-UI-03: abrir /inventory.html sin sesión redirige al login con un error."""
    InventoryPage(driver).open()

    error = LoginPage(driver).get_error_message()
    assert "You can only access '/inventory.html' when you are logged in." in error
