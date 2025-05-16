import glob
import logging
import os
import time
from typing import Union, Optional, List, Dict
from selenium import webdriver
from selenium.common import TimeoutException, NoSuchWindowException, NoSuchFrameException, WebDriverException, \
    NoSuchElementException, ElementNotInteractableException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
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

def clickar_boton_por_id(driver: webdriver.Chrome, id: str, timeout: int = DEFAULT_TIMEOUT) -> None:
    """Espera y hace clic en un botón (elemento input) que tiene el ID especificado."""
    clickar_elemento(driver, By.ID, id, timeout)

def clickar_boton_por_value(driver: webdriver.Chrome, value: str, timeout: int = DEFAULT_TIMEOUT) -> None:
    """Espera y hace clic en un botón (elemento input) que tiene el atributo 'value' especificado."""
    selector = f"input[value='{value}']"
    clickar_elemento(driver, By.CSS_SELECTOR, selector, timeout)

def clickar_boton_por_texto(driver: webdriver.Chrome, texto: str, timeout: int = DEFAULT_TIMEOUT) -> None:
    """Espera y hace clic en un botón (elemento span) que contiene el texto especificado."""
    xpath = f"//span[contains(text()='{texto}')]"
    clickar_elemento(driver, By.XPATH, xpath, timeout)
def clickar_boton_por_link(driver: webdriver.Chrome, link: str, timeout: int = DEFAULT_TIMEOUT) -> None:
    xpath =  f"//a[contains(text(), '{link}')]"
    clickar_elemento(driver, By.XPATH, xpath, timeout)

def clickar_boton_por_clase(driver: webdriver.Chrome, clase: str, timeout: int = DEFAULT_TIMEOUT):
    # Busca el primer elemento con esa clase
    selector = f".{clase}"
    clickar_elemento(driver, By.CSS_SELECTOR, selector, timeout)

def abrir_nueva_pestana(driver: webdriver.Chrome, url: str) -> bool:
    """
    Abre una nueva pestaña con la URL especificada y cambia el foco a ella.

    Args:
        driver (webdriver.Chrome): Instancia del navegador.
        url (str): URL que se abrirá en la nueva pestaña.

    Returns:
        bool: True si la operación fue exitosa, False si falló.

    Ejemplo:
        abrir_nueva_pestana(driver, "https://example.com")
    """
    try:
        # Guardar handle actual
        handle_actual = driver.current_window_handle

        # Abrir nueva pestaña con la URL
        driver.execute_script(f"window.open('{url}', '_blank');")
        logging.info(f"Se abrió una nueva pestaña con la URL: {url}")

        # Obtener todos los handles y cambiar al último (la nueva pestaña)
        handles = driver.window_handles
        nuevas = [h for h in handles if h != handle_actual]
        if nuevas:
            driver.switch_to.window(nuevas[-1])
            logging.info(f"Foco cambiado a la nueva pestaña.")
            return True
        else:
            logging.warning("No se detectó una nueva pestaña después de abrirla.")
            return False

    except WebDriverException as e:
        logging.error(f"Error al abrir nueva pestaña con URL '{url}': {e}")
        return False

def cambiar_a_ventana(driver: webdriver.Chrome, indice: int) -> None:
    """
    Cambia el enfoque del navegador a la ventana/pestaña según el índice proporcionado.

    Args:
        driver (webdriver.Chrome): Instancia del navegador.
        indice (int): Índice de la ventana a la que se desea cambiar.

    Raises:
        IndexError: Si el índice está fuera del rango de las ventanas abiertas.
        NoSuchWindowException: Si la ventana no se puede encontrar.

    Ejemplo:
        cambiar_a_ventana(driver, 1)
    """
    try:
        handles = driver.window_handles
        driver.switch_to.window(handles[indice])
        logging.info(f"Cambiado a la pestaña con nombre '{driver.title}'")
    except IndexError:
        raise IndexError(f"Índice de ventana inválido: {indice}. Solo hay {len(driver.window_handles)} ventanas.")
    except NoSuchWindowException as e:
        raise logging.error(f"No se pudo cambiar a la ventana: {e}")

def capturar_pantalla(driver: webdriver.Chrome, ruta_archivo: str, timeout: int = 10) -> bool:
    """
    Espera a que la página se cargue completamente y guarda una captura de pantalla en el archivo especificado.

    Args:
        driver (webdriver.Chrome): Instancia del navegador.
        ruta_archivo (str): Ruta donde se guardará la imagen (PNG).
        timeout (int): Tiempo máximo de espera para la carga de la página (en segundos). Por defecto, 10.

    Returns:
        bool: True si la captura fue exitosa, False si falló.

    Ejemplo:
        capturar_pantalla(driver, "screenshots/pagina.png")
    """
    try:
        # Esperar a que el DOM esté completamente cargado
        WebDriverWait(driver, timeout).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        logging.info("La página se cargó completamente antes de la captura.")

        # Crear directorio si no existe
        os.makedirs(os.path.dirname(ruta_archivo), exist_ok=True)

        # Capturar pantalla
        exito = driver.get_screenshot_as_file(ruta_archivo)
        if exito:
            logging.info(f"Captura de pantalla guardada en: {ruta_archivo}")
        else:
            logging.warning(f"No se pudo guardar la captura en: {ruta_archivo}")
        return exito

    except WebDriverException as e:
        logging.error(f"Error al capturar pantalla: {e}")
        return False

    except Exception as e:
        logging.error(f"Error inesperado al esperar la carga o capturar pantalla: {e}")
        return False

def obtener_logs_navegador(driver: webdriver.Chrome) -> List[Dict]:
    """
    Obtiene los logs del navegador (nivel 'browser') si están habilitados en las opciones del navegador.

    Args:
        driver (webdriver.Chrome): Instancia del navegador.

    Returns:
        List[Dict]: Lista de entradas de log capturadas, cada una como un diccionario.

    Nota:
        Para que esto funcione, debes habilitar los logs al iniciar el navegador con:
            options.set_capability('goog:loggingPrefs', {'browser': 'ALL'})

    Ejemplo:
        logs = obtener_logs_navegador(driver)
        for log in logs:
            print(log["message"])
    """
    try:
        logs = driver.get_log("browser")
        return logs
    except WebDriverException as e:
        logging.error(f"No se pudieron obtener los logs del navegador: {e}")
        return []

def escribir_en_elemento(driver: webdriver.Chrome, by: By, value: str, texto: str, timeout: int = DEFAULT_TIMEOUT) -> None:
    """
    Encuentra un campo de entrada y escribe el texto indicado en él.

    Args:
        driver (webdriver.Chrome): Instancia del navegador.
        by (By): Tipo de localizador (By.ID, By.XPATH, etc.).
        value (str): Valor del selector.
        texto (str): Texto que se desea escribir.
        timeout (int): El tiempo máximo de espera en segundos.

    Raises:
        Exception: Si el elemento no se encuentra o no se puede interactuar.

    Ejemplo:
        escribir_en_elemento(driver, By.NAME, "usuario", "admin")
    """
    try:
        esperar_elemento(driver, by, value, timeout)
        elemento = driver.find_element(by, value)
        elemento.send_keys(texto)
        logging.info(f"Se escribió texto en el elemento localizado por {by}='{value}': '{texto}'")

    except TimeoutException:
        raise

    except NoSuchElementException:
        logging.error(f"No se encontró el elemento con {by}='{value}' para escribir.")
        raise

    except ElementNotInteractableException:
        logging.error(f"El elemento con {by}='{value}' no es interactuable.")
        raise

    except Exception as e:
        logging.error(f"Error inesperado al escribir en el elemento: {e}")
        raise
def escribir_en_elemento_por_id(driver: webdriver.Chrome, element_id: str, texto: str) -> None:
    """Espera hasta que un elemento con el ID especificado sea visible."""
    try:
        escribir_en_elemento(driver, By.ID, element_id, texto)
    except Exception as e:
        logging.error(f"No se pudo escribir en el elemento con ID '{element_id}': {e}")
        raise

def escribir_en_elemento_por_name(driver: webdriver.Chrome, name: str, texto: str) -> None:
    """Espera hasta que un elemento con el atributo name especificado sea visible y escribe texto en él."""
    try:
        escribir_en_elemento(driver, By.NAME, name, texto)
    except Exception as e:
        logging.error(f"No se pudo escribir en el elemento con name '{name}': {e}")
        raise

def escribir_en_elemento_por_placeholder(driver: webdriver.Chrome, placeholder_text: str, texto: str) -> None:
    """Escribe texto en un campo de entrada localizado por su atributo placeholder."""
    try:
        xpath = f"//*[@placeholder='{placeholder_text}']"
        escribir_en_elemento(driver, By.XPATH, xpath, texto)
    except Exception as e:
        logging.error(f"No se pudo escribir en el elemento con placeholder '{placeholder_text}': {e}")
        raise

def escribir_en_elemento_por_class(driver: webdriver.Chrome, class_name: str, texto: str) -> None:
    """Escribe texto en un elemento localizado por su clase CSS."""
    try:
        escribir_en_elemento(driver, By.CLASS_NAME, class_name, texto)
    except Exception as e:
        logging.error(f"No se pudo escribir en el elemento con class '{class_name}': {e}")
        raise

def aceptarAlerta(driver):
    try:
        WebDriverWait(driver, 5).until(EC.alert_is_present())
        alert = driver.switch_to.alert
        alert.accept()
        logging.info("Alerta aceptada correctamente.")
    except TimeoutException:
        logging.error("No hay alerta presente.")

def seleccionar_elemento(driver: webdriver.Chrome, by: By, value: str, opcion: str,
                         timeout: int = DEFAULT_TIMEOUT) -> None:
    try:
        # Se espera a que el elemento <select> esté presente en la página.
        esperar_elemento(driver, by, value, timeout)
        # Se localiza el elemento <select> y se crea el objeto Select.
        elemento = driver.find_element(by, value)
        select_obj = Select(elemento)
        # Se selecciona la opción cuyo texto visible coincida con 'opcion'.
        select_obj.select_by_visible_text(opcion)
        logging.info(f"Opción '{opcion}' seleccionada en el elemento con '{by}' = '{value}'.")
    except TimeoutException:
        raise
    except Exception as e:
        logging.error(f"Falló al seleccionar la opción '{opcion}' en el elemento con '{by}' = '{value}': {e}")
        raise

def seleccionar_elemento_por_texto(driver: webdriver.Chrome, by: By, value: str, texto: str, timeout: int = DEFAULT_TIMEOUT) -> None:
    """Selecciona una opción de un <select> localizado por 'by' y 'value', usando el texto visible 'texto'."""
    seleccionar_elemento(driver, by, value, texto, timeout)

def seleccionar_elemento_por_class(driver: webdriver.Chrome, class_name: str, texto: str, timeout: int = DEFAULT_TIMEOUT) -> None:
    """Selecciona una opción de un <select> localizado por clase CSS, usando el texto visible 'texto'."""
    seleccionar_elemento(driver, By.CLASS_NAME, class_name, texto, timeout)

def seleccionar_elemento_por_id(driver: webdriver.Chrome, element_id: str, opcion: str, timeout: int = DEFAULT_TIMEOUT) -> None:
    seleccionar_elemento(driver, By.ID, element_id, opcion, timeout)

def seleccionar_elemento_por_nombre(driver: webdriver.Chrome, name: str, opcion: str, timeout: int = DEFAULT_TIMEOUT) -> None:
    seleccionar_elemento(driver, By.NAME, name, opcion, timeout)

def seleccionar_elemento_por_tag_name(driver: webdriver.Chrome, tag_name: str, opcion: str, timeout: int = DEFAULT_TIMEOUT) -> None:
    seleccionar_elemento(driver, By.TAG_NAME, tag_name, opcion, timeout)

def aceptar_pop_up(driver: webdriver.Chrome, pop_up: str, boton: str) -> None:
    """Acepta el pop-up de descarga de Excel."""
    popup_div = driver.find_element(By.ID, pop_up)
    boton_aceptar = popup_div.find_element(By.CLASS_NAME, boton)
    boton_aceptar.click()

