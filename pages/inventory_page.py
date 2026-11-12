"""Page Object del catálogo de productos (inventory.html)."""
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

from pages.base_page import BasePage


class InventoryPage(BasePage):
    PATH = "/inventory.html"

    INVENTORY_LIST = (By.CSS_SELECTOR, "div.inventory_list")
    PRODUCT_CARDS = (By.CSS_SELECTOR, "div.inventory_item")
    PRODUCT_NAME = (By.CSS_SELECTOR, "div.inventory_item_name")
    PRODUCT_PRICE = (By.CSS_SELECTOR, "div.inventory_item_price")
    PRODUCT_BUTTON = (By.CSS_SELECTOR, "button.btn_inventory")
    SORT_SELECT = (By.CSS_SELECTOR, "select.product_sort_container")

    def wait_until_loaded(self):
        self.wait_for_url_contains("inventory.html")
        self.find_visible(self.INVENTORY_LIST)
        self.wait_for_elements(self.PRODUCT_CARDS)
        return self

    def is_sort_dropdown_visible(self) -> bool:
        return self.is_visible(self.SORT_SELECT)

    def is_menu_visible(self) -> bool:
        return self.is_visible(self.MENU_BUTTON)

    # ---------- Lectura del catálogo ----------
    def get_product_names(self) -> list[str]:
        return self.get_texts(self.PRODUCT_NAME)

    def get_product_prices(self) -> list[float]:
        """Precios como números (por ejemplo '$29.99' -> 29.99)."""
        return [float(price.replace("$", "")) for price in self.get_texts(self.PRODUCT_PRICE)]

    def get_price_of(self, product_name: str) -> float:
        price_text = self.retry_on_stale(
            lambda: self._find_product_card(product_name).find_element(*self.PRODUCT_PRICE).text)
        return float(price_text.replace("$", ""))

    # ---------- Acciones ----------
    def sort_by(self, option_value: str):
        """Ordena el catálogo. Valores posibles: az, za, lohi, hilo."""
        self.logger.info("Ordenando productos por '%s'", option_value)
        Select(self.find_visible(self.SORT_SELECT)).select_by_value(option_value)

    def add_product_to_cart(self, product_name: str):
        self.logger.info("Agregando al carrito: %s", product_name)
        self._click_product_button(product_name, expected_label_after="Remove")

    def remove_product_from_cart(self, product_name: str):
        self.logger.info("Quitando del carrito desde el catálogo: %s", product_name)
        self._click_product_button(product_name, expected_label_after="Add to cart")

    # ---------- Métodos internos ----------
    def _find_product_card(self, product_name: str):
        for card in self.find_all(self.PRODUCT_CARDS):
            if card.find_element(*self.PRODUCT_NAME).text == product_name:
                return card
        raise ValueError(f"El producto '{product_name}' no está en el catálogo")

    def _product_button(self, product_name: str):
        """Busca el botón cada vez: tras un clic React puede reemplazar la tarjeta."""
        return self._find_product_card(product_name).find_element(*self.PRODUCT_BUTTON)

    def _click_product_button(self, product_name: str, expected_label_after: str):
        self.retry_on_stale(lambda: self._product_button(product_name).click())
        # Espera a que el botón cambie de estado para confirmar la acción
        self.wait.until(lambda _: self._product_button(product_name).text == expected_label_after)
