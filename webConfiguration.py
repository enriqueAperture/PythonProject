import loggerConfig
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


def configure():
    # Configurar el WebDriver para Google Chrome
    options = Options()
    try:
        # Asigna el perfil donde ya está instalado el certificado
        options.add_argument(r"--user-data-dir=C:\Users\Usuario\AppData\Local\Google\Chrome\User Data")
        options.add_argument("--profile-directory=Default")
    except AttributeError:
        logging.error("Ha habido un error")

    # Opcional: para que veas errores o popups
    #options.add_argument("--headless")  # puedes quitarlo temporalmente

    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-infobars")
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        logging.info("Inicializando navegador...")
        return driver
    except Exception as e:
        logging.error(f"Error al iniciar el navegador: {e}")
        return None