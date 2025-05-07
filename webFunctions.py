import logging
from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

# Configuración del tiempo de espera global (en segundos)
DEFAULT_TIMEOUT = 5

def abrir_web(driver: webdriver.Chrome, url: str) -> None:
    """Abre la URL especificada en el navegador.

    Args:
        driver: El objeto WebDriver de Chrome.
        url: La URL a abrir.
    """
    driver.get(url)
    logging.info(f"Web '{url}' abierta.")

def esperar_elemento(driver: webdriver.Chrome, by: By, value: str, timeout: int = DEFAULT_TIMEOUT) -> WebDriverWait:
    """Espera hasta que un elemento sea visible utilizando la estrategia de localización dada.

    Args:
        driver: El objeto WebDriver de Chrome.
        by: La estrategia de localización como string ('id', 'xpath', 'css selector', etc.).
        value: El valor del localizador.
        timeout: El tiempo máximo de espera en segundos.

    Returns:
        El objeto WebDriverWait.

    Raises:
        TimeoutException: Si el elemento no se encuentra dentro del tiempo de espera.
    """
    if not by:
        raise ValueError(f"Estrategia de localización '{by}' no válida. Debe ser uno de: 'id', 'xpath', 'css selector', etc.")

    wait = WebDriverWait(driver, timeout)
    try:
        wait.until(EC.visibility_of_element_located((by, value)))
        return wait
    except TimeoutException:
        logging.error(f"Timeout al esperar el elemento con '{by}' = '{value}'")
        raise

def clickar_elemento(driver: webdriver.Chrome, by: By, value: str, timeout: int = DEFAULT_TIMEOUT) -> None:
    """Espera y hace clic en un elemento utilizando la estrategia de localización dada.

    Args:
        driver: El objeto WebDriver de Chrome.
        by: La estrategia de localización como string ('id', 'xpath', 'css selector', etc.).
        value: El valor del localizador.
        timeout: El tiempo máximo de espera en segundos.

    Raises:
        TimeoutException: Si el elemento no se encuentra dentro del tiempo de espera.
        Exception: Si ocurre un error al intentar hacer clic.
    """
    try:
        esperar_elemento(driver, by, value, timeout)
        elemento = driver.find_element(by, value)
        elemento.click()
        logging.info(f"Elemento clickado con '{by}' = '{value}'.")
    except TimeoutException:
        raise
    except Exception as e:
        logging.error(f"Falló al clickar el elemento con '{by}' = '{value}': '{e}'")
        raise

def esperar_elemento_por_id(driver: webdriver.Chrome, element_id: str, timeout: int = DEFAULT_TIMEOUT) -> None:
    """Espera hasta que un elemento con el ID especificado sea visible."""
    esperar_elemento(driver, By.ID, element_id, timeout)

def clickar_boton_por_value(driver: webdriver.Chrome, value: str, timeout: int = DEFAULT_TIMEOUT) -> None:
    """Espera y hace clic en un botón (elemento input) que tiene el atributo 'value' especificado."""
    selector = f"input[value='{value}']"
    clickar_elemento(driver, By.CSS_SELECTOR, selector, timeout)

def clickar_boton_por_texto(driver: webdriver.Chrome, texto: str, timeout: int = DEFAULT_TIMEOUT) -> None:
    """Espera y hace clic en un botón (elemento span) que contiene el texto especificado."""
    xpath = f"//span[text()='{texto}']"
    clickar_elemento(driver, By.XPATH, xpath, timeout)