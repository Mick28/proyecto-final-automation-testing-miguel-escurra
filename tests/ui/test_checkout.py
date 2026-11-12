"""Casos de prueba del flujo completo de compra (checkout)."""
import pytest

from pages.cart_page import CartPage
from pages.checkout_pages import CheckoutCompletePage, CheckoutInformationPage, CheckoutOverviewPage
from utils.data_loader import read_json

pytestmark = pytest.mark.ui

CHECKOUT_DATA = read_json("checkout_data.json")
VALID_PURCHASES = [pytest.param(c, id=c["caso"]) for c in CHECKOUT_DATA["compras_validas"]]
INCOMPLETE_DATA = [pytest.param(c, id=c["caso"]) for c in CHECKOUT_DATA["datos_incompletos"]]


@pytest.mark.smoke
@pytest.mark.parametrize("purchase", VALID_PURCHASES)
def test_compra_completa(driver, inventory_page, purchase):
    """TC-UI-08: flujo end-to-end login -> carrito -> checkout -> confirmación, validando totales."""
    expected_subtotal = 0.0
    for product in purchase["productos"]:
        expected_subtotal += inventory_page.get_price_of(product)
        inventory_page.add_product_to_cart(product)

    inventory_page.go_to_cart()
    CartPage(driver).go_to_checkout()

    CheckoutInformationPage(driver).fill_information(
        purchase["nombre"], purchase["apellido"], purchase["codigo_postal"])

    overview = CheckoutOverviewPage(driver).wait_until_loaded()
    assert sorted(overview.get_item_names()) == sorted(purchase["productos"])
    assert overview.get_subtotal() == pytest.approx(expected_subtotal)
    assert overview.get_total() == pytest.approx(overview.get_subtotal() + overview.get_tax())

    overview.finish()
    complete = CheckoutCompletePage(driver)
    assert complete.get_confirmation_message() == "Thank you for your order!"
    assert complete.get_cart_count() == 0, "El carrito debería quedar vacío tras la compra"


@pytest.mark.negative
@pytest.mark.parametrize("buyer", INCOMPLETE_DATA)
def test_checkout_con_datos_incompletos(driver, inventory_page, buyer):
    """TC-UI-09: el checkout no avanza y muestra el error si falta un dato obligatorio."""
    inventory_page.add_product_to_cart("Sauce Labs Onesie")
    inventory_page.go_to_cart()
    CartPage(driver).go_to_checkout()

    information = CheckoutInformationPage(driver)
    information.fill_information(buyer["nombre"], buyer["apellido"], buyer["codigo_postal"])

    assert information.get_error_message() == buyer["mensaje_error"]
    assert "checkout-step-one.html" in driver.current_url
