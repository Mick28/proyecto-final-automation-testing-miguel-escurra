"""Page Object del carrito de compras (cart.html)."""
from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class CartPage(BasePage):
    PATH = "/cart.html"

    CART_ITEMS = (By.CSS_SELECTOR, "div.cart_item")
    ITEM_NAME = (By.CSS_SELECTOR, "div.inventory_item_name")
    ITEM_NAMES = (By.CSS_SELECTOR, "div.cart_item div.inventory_item_name")
    REMOVE_BUTTON = (By.CSS_SELECTOR, "button.cart_button")
    CHECKOUT_BUTTON = (By.ID, "checkout")
    CONTINUE_SHOPPING_BUTTON = (By.ID, "continue-shopping")

    def wait_until_loaded(self):
        """La página está lista cuando se dibujó el botón Checkout."""
        self.find_visible(self.CHECKOUT_BUTTON)
        return self

    def get_item_names(self) -> list[str]:
        self.wait_until_loaded()
        return self.get_texts(self.ITEM_NAMES)

    def remove_item(self, product_name: str):
        self.logger.info("Quitando del carrito: %s", product_name)
        self.wait_until_loaded()
        items_before = len(self.find_all(self.CART_ITEMS))
        self.retry_on_stale(lambda: self._remove_button_of(product_name).click())
        # Confirma que el ítem desapareció de la lista
        self.wait.until(lambda _: len(self.find_all(self.CART_ITEMS)) == items_before - 1)

    def _remove_button_of(self, product_name: str):
        for item in self.find_all(self.CART_ITEMS):
            if item.find_element(*self.ITEM_NAME).text == product_name:
                return item.find_element(*self.REMOVE_BUTTON)
        raise ValueError(f"El producto '{product_name}' no está en el carrito")

    def go_to_checkout(self):
        self.logger.info("Iniciando checkout")
        self.click(self.CHECKOUT_BUTTON)
        self.wait_for_url_contains("checkout-step-one.html")

    def continue_shopping(self):
        self.click(self.CONTINUE_SHOPPING_BUTTON)
        self.wait_for_url_contains("inventory.html")
