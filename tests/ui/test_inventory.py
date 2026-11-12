"""Casos de prueba de navegación y búsqueda/ordenamiento en el catálogo."""
import pytest

from utils.data_loader import read_json

pytestmark = pytest.mark.ui

SORT_CASES = [pytest.param(case, id=case["opcion"]) for case in read_json("sort_options.json")]


@pytest.mark.smoke
def test_catalogo_muestra_elementos_principales(inventory_page):
    """TC-UI-04: el catálogo muestra título, productos con nombre y precio, menú y filtro."""
    names = inventory_page.get_product_names()
    prices = inventory_page.get_product_prices()

    assert inventory_page.get_page_title() == "Products"
    assert len(names) == 6, f"Se esperaban 6 productos y hay {len(names)}"
    assert all(name.strip() for name in names), "Hay productos sin nombre"
    assert all(price > 0 for price in prices), "Hay productos sin precio válido"
    assert inventory_page.is_menu_visible(), "No se ve el menú lateral"
    assert inventory_page.is_sort_dropdown_visible(), "No se ve el filtro de ordenamiento"
    assert inventory_page.get_cart_count() == 0, "El carrito debería empezar vacío"


@pytest.mark.parametrize("sort_case", SORT_CASES)
def test_ordenar_catalogo(inventory_page, sort_case):
    """TC-UI-05: el filtro ordena los productos por nombre o precio en ambos sentidos."""
    inventory_page.sort_by(sort_case["opcion"])

    if sort_case["campo"] == "nombre":
        values = inventory_page.get_product_names()
    else:
        values = inventory_page.get_product_prices()

    expected = sorted(values, reverse=sort_case["descendente"])
    assert values == expected, f"Orden incorrecto para '{sort_case['opcion']}': {values}"
