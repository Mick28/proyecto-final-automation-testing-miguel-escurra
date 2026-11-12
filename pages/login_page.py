"""Page Object de la pantalla de login de SauceDemo."""
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class LoginPage(BasePage):
    PATH = "/"

    USERNAME_INPUT = (By.ID, "user-name")
    PASSWORD_INPUT = (By.ID, "password")
    LOGIN_BUTTON = (By.ID, "login-button")
    ERROR_MESSAGE = (By.CSS_SELECTOR, "h3[data-test='error']")

    def login(self, username: str, password: str):
        """Completa el formulario y presiona Login."""
        self.logger.info("Login con usuario '%s'", username or "<vacío>")
        self.type_text(self.USERNAME_INPUT, username)
        self.type_text(self.PASSWORD_INPUT, password)
        self.click(self.LOGIN_BUTTON)

    def get_error_message(self) -> str:
        message = self.get_text(self.ERROR_MESSAGE)
        self.logger.info("Mensaje de error mostrado: %s", message)
        return message

    def is_displayed(self) -> bool:
        """True si el formulario de login aparece (espera la navegación, por ejemplo tras un logout)."""
        try:
            self.find_visible(self.LOGIN_BUTTON)
            return True
        except TimeoutException:
            return False
