import loggerConfig
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


def configure():
    # Configurar el WebDriver para Google Chrome
    options = Options()
    options.add_argument("--start-maximized")  # Maximiza la ventana
    options.add_argument("--disable-notifications")  # Desactiva notificaciones
    options.add_argument("--disable-infobars")  # Oculta el "Chrome is being controlled..."
    #options.add_argument("--headless")  # (opcional) Ejecuta sin abrir ventana

    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        logging.info("Inicializando navegador...")
        return driver
    except Exception as e:
        logging.error(f"Error al iniciar el navegador: {e}")
        return None