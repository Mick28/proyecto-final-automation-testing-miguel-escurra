"""Casos de prueba del carrito de compras."""
import pytest

from pages.cart_page import CartPage
from utils.data_loader import read_json

pytestmark = pytest.mark.ui

CART_CASES = [pytest.param(case["productos"], id=case["caso"]) for case in read_json("cart_products.json")]


@pytest.mark.smoke
@pytest.mark.parametrize("products", CART_CASES)
def test_agregar_productos_al_carrito(driver, inventory_page, products):
    """TC-UI-06: el badge cuenta los productos agregados y el carrito los lista."""
    for product in products:
        inventory_page.add_product_to_cart(product)

    assert inventory_page.get_cart_count() == len(products)

    inventory_page.go_to_cart()
    cart = CartPage(driver)
    assert cart.get_page_title() == "Your Cart"
    assert sorted(cart.get_item_names()) == sorted(products)


def test_quitar_producto_del_carrito(driver, inventory_page):
    """TC-UI-07: quitar un producto desde el carrito actualiza la lista y el contador."""
    inventory_page.add_product_to_cart("Sauce Labs Backpack")
    inventory_page.add_product_to_cart("Sauce Labs Bike Light")
    inventory_page.go_to_cart()

    cart = CartPage(driver)
    cart.remove_item("Sauce Labs Backpack")

    assert cart.get_item_names() == ["Sauce Labs Bike Light"]
    assert cart.get_cart_count() == 1
