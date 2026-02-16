from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
import config.settings as settings
from src.utils import setup_logging

logger = setup_logging()


class BrowserManager:
    """Gerencia o navegador Chrome/Selenium"""

    def __init__(self, headless=None):
        self.headless = headless if headless is not None else settings.HEADLESS
        self.driver = None
        self.wait = None

    def start(self):
        """Inicializa o navegador"""
        try:
            logger.info("Iniciando navegador...")

            # Configurações do Chrome
            chrome_options = Options()

            if self.headless:
                chrome_options.add_argument("--headless=new")

            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-popup-blocking")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option(
                "excludeSwitches", ["enable-automation"]
            )
            chrome_options.add_experimental_option("useAutomationExtension", False)

            # Inicializa o driver
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.execute_script(
                "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
            )

            # Configura wait
            self.wait = WebDriverWait(self.driver, settings.BROWSER_TIMEOUT)

            logger.info("Navegador iniciado com sucesso!")
            return self.driver

        except Exception as e:
            logger.error(f"Erro ao iniciar navegador: {e}")
            raise

    def quit(self):
        """Fecha o navegador"""
        if self.driver:
            logger.info("Fechando navegador...")
            self.driver.quit()
            self.driver = None

    def wait_for_element(self, locator, timeout=None):
        """Aguarda elemento ficar visível"""
        wait_time = timeout or settings.BROWSER_TIMEOUT
        wait = WebDriverWait(self.driver, wait_time)
        return wait.until(EC.visibility_of_element_located(locator))

    def wait_for_clickable(self, locator, timeout=None):
        """Aguarda elemento ficar clicável"""
        wait_time = timeout or settings.BROWSER_TIMEOUT
        wait = WebDriverWait(self.driver, wait_time)
        return wait.until(EC.element_to_be_clickable(locator))

    def safe_click(self, locator):
        """Clica em elemento com tratamento de erro"""
        try:
            element = self.wait_for_clickable(locator)
            element.click()
            return True
        except Exception as e:
            logger.error(f"Erro ao clicar: {e}")
            return False

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.quit()
