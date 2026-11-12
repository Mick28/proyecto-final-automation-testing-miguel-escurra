"""Page Objects de las tres pantallas del checkout de SauceDemo.

1. CheckoutInformationPage -> checkout-step-one.html (datos del comprador)
2. CheckoutOverviewPage    -> checkout-step-two.html (resumen y totales)
3. CheckoutCompletePage    -> checkout-complete.html (confirmación)
"""
import re

from selenium.webdriver.common.by import By

from pages.base_page import BasePage


def _extract_amount(text: str) -> float:
    """Convierte textos como 'Item total: $39.98' en 39.98."""
    match = re.search(r"\$([\d.]+)", text)
    if not match:
        raise ValueError(f"No se encontró un importe en '{text}'")
    return float(match.group(1))


class CheckoutInformationPage(BasePage):
    PATH = "/checkout-step-one.html"

    FIRST_NAME_INPUT = (By.ID, "first-name")
    LAST_NAME_INPUT = (By.ID, "last-name")
    POSTAL_CODE_INPUT = (By.ID, "postal-code")
    CONTINUE_BUTTON = (By.ID, "continue")
    ERROR_MESSAGE = (By.CSS_SELECTOR, "h3[data-test='error']")

    def fill_information(self, first_name: str, last_name: str, postal_code: str):
        self.logger.info("Completando datos del comprador: '%s' '%s' CP '%s'",
                         first_name, last_name, postal_code)
        self.type_text(self.FIRST_NAME_INPUT, first_name)
        self.type_text(self.LAST_NAME_INPUT, last_name)
        self.type_text(self.POSTAL_CODE_INPUT, postal_code)
        self.click(self.CONTINUE_BUTTON)

    def get_error_message(self) -> str:
        message = self.get_text(self.ERROR_MESSAGE)
        self.logger.info("Mensaje de error mostrado: %s", message)
        return message


class CheckoutOverviewPage(BasePage):
    PATH = "/checkout-step-two.html"

    ITEM_NAMES = (By.CSS_SELECTOR, "div.cart_item div.inventory_item_name")
    SUBTOTAL_LABEL = (By.CSS_SELECTOR, "div.summary_subtotal_label")
    TAX_LABEL = (By.CSS_SELECTOR, "div.summary_tax_label")
    TOTAL_LABEL = (By.CSS_SELECTOR, "div.summary_total_label")
    FINISH_BUTTON = (By.ID, "finish")

    def wait_until_loaded(self):
        """Espera la URL, el botón Finish y que se dibuje al menos un producto."""
        self.wait_for_url_contains("checkout-step-two.html")
        self.find_visible(self.FINISH_BUTTON)
        self.wait_for_elements(self.ITEM_NAMES)
        return self

    def get_item_names(self) -> list[str]:
        return self.get_texts(self.ITEM_NAMES)

    def get_subtotal(self) -> float:
        return _extract_amount(self.get_text(self.SUBTOTAL_LABEL))

    def get_tax(self) -> float:
        return _extract_amount(self.get_text(self.TAX_LABEL))

    def get_total(self) -> float:
        return _extract_amount(self.get_text(self.TOTAL_LABEL))

    def finish(self):
        self.logger.info("Confirmando la compra (Finish)")
        self.click(self.FINISH_BUTTON)
        self.wait_for_url_contains("checkout-complete.html")


class CheckoutCompletePage(BasePage):
    PATH = "/checkout-complete.html"

    COMPLETE_HEADER = (By.CSS_SELECTOR, "h2.complete-header")
    BACK_HOME_BUTTON = (By.ID, "back-to-products")

    def get_confirmation_message(self) -> str:
        return self.get_text(self.COMPLETE_HEADER)

    def back_to_products(self):
        self.click(self.BACK_HOME_BUTTON)
        self.wait_for_url_contains("inventory.html")
