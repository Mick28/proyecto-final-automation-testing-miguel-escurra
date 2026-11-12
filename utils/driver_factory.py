"""Creación del WebDriver de Chrome con la configuración del framework."""
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

from utils import config
from utils.logger import get_logger

logger = get_logger("driver_factory")


def create_chrome_driver(headless: bool = config.HEADLESS) -> webdriver.Chrome:
    """Crea una instancia nueva de Chrome lista para usar en un test."""
    options = webdriver.ChromeOptions()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--no-sandbox")             # necesario en runners Linux de CI
    options.add_argument("--disable-dev-shm-usage")  # evita falta de memoria compartida en contenedores
    options.add_argument("--incognito")
    # Desactiva el gestor de contraseñas: en SauceDemo Chrome muestra un aviso
    # de "contraseña filtrada" que tapa la página y rompe los tests.
    options.add_experimental_option("prefs", {
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False,
        "profile.password_manager_leak_detection": False,
    })

    # Si CHROMEDRIVER_PATH no está definido, Selenium Manager descarga el driver correcto
    service = Service(config.CHROMEDRIVER_PATH) if config.CHROMEDRIVER_PATH else Service()
    driver = webdriver.Chrome(service=service, options=options)
    logger.info("Chrome iniciado (headless=%s, versión %s)",
                headless, driver.capabilities.get("browserVersion"))
    return driver
