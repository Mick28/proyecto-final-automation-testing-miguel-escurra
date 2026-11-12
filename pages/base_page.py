"""Clase base de todos los Page Objects.

Concentra las acciones genéricas (esperar, hacer clic, escribir, leer)
y los elementos del encabezado que comparten todas las páginas internas
de SauceDemo (carrito y menú lateral). Así cada página hija solo define
sus propios locators y acciones de negocio.
"""
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from utils import config
from utils.logger import get_logger


class BasePage:
    # Ruta relativa de la página (cada Page Object define la suya)
    PATH = "/"

    # Encabezado común a las páginas internas
    PAGE_TITLE = (By.CSS_SELECTOR, "span.title")
    CART_LINK = (By.CSS_SELECTOR, "a.shopping_cart_link")
    CART_BADGE = (By.CSS_SELECTOR, "span.shopping_cart_badge")
    MENU_BUTTON = (By.ID, "react-burger-menu-btn")
    LOGOUT_LINK = (By.ID, "logout_sidebar_link")

    def __init__(self, driver: WebDriver):
        self.driver = driver
        # SauceDemo está hecho en React: al cambiar el estado vuelve a dibujar
        # elementos y las referencias viejas quedan "stale". La espera ignora
        # ese error y vuelve a buscar el elemento en el siguiente intento.
        self.wait = WebDriverWait(driver, config.EXPLICIT_WAIT,
                                  ignored_exceptions=[StaleElementReferenceException])
        self.logger = get_logger(f"pages.{self.__class__.__name__}")

    # ---------- Navegación ----------
    def open(self):
        url = f"{config.BASE_URL}{self.PATH}"
        self.logger.info("Abriendo %s", url)
        self.driver.get(url)
        return self

    @property
    def current_url(self) -> str:
        return self.driver.current_url

    # ---------- Acciones genéricas con espera explícita ----------
    def find_visible(self, locator) -> WebElement:
        return self.wait.until(EC.visibility_of_element_located(locator))

    def find_all(self, locator) -> list[WebElement]:
        """Devuelve todos los elementos que coinciden (lista vacía si no hay)."""
        return self.driver.find_elements(*locator)

    def get_texts(self, locator) -> list[str]:
        """Textos de todos los elementos que coinciden (lista vacía si no hay)."""
        return self.retry_on_stale(lambda: [element.text for element in self.find_all(locator)])

    @staticmethod
    def retry_on_stale(action, attempts: int = 3):
        """Ejecuta 'action' y, si la página se re-renderizó en el medio, lo reintenta."""
        for attempt in range(1, attempts + 1):
            try:
                return action()
            except StaleElementReferenceException:
                if attempt == attempts:
                    raise

    def wait_for_elements(self, locator) -> list[WebElement]:
        """Espera a que exista al menos un elemento visible y devuelve todos."""
        return self.wait.until(EC.visibility_of_any_elements_located(locator))

    def click(self, locator):
        self.wait.until(EC.element_to_be_clickable(locator)).click()

    def type_text(self, locator, text: str):
        field = self.find_visible(locator)
        field.clear()
        field.send_keys(text)

    def get_text(self, locator) -> str:
        return self.retry_on_stale(lambda: self.find_visible(locator).text)

    def is_visible(self, locator) -> bool:
        elements = self.find_all(locator)
        return bool(elements) and elements[0].is_displayed()

    def wait_for_url_contains(self, fragment: str):
        self.wait.until(EC.url_contains(fragment))

    # ---------- Encabezado compartido ----------
    def get_page_title(self) -> str:
        return self.get_text(self.PAGE_TITLE)

    def get_cart_count(self) -> int:
        """Cantidad del badge del carrito (0 si el badge no se muestra)."""
        badges = self.find_all(self.CART_BADGE)
        return int(badges[0].text) if badges else 0

    def go_to_cart(self):
        self.logger.info("Ingresando al carrito")
        self.click(self.CART_LINK)
        self.wait_for_url_contains("cart.html")

    def logout(self):
        self.logger.info("Cerrando sesión desde el menú lateral")
        self.click(self.MENU_BUTTON)
        self.click(self.LOGOUT_LINK)
