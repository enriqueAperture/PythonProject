import loggerConfig
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.support.wait import WebDriverWait


def abrir_web(driver: webdriver.Chrome, url: str):
    driver.get(url)
    logging.info(f"Web '{url}' abierta.")

def esperar_elemento_por_id(driver: webdriver.Chrome, id: str):
    try:
        wait = WebDriverWait(driver, 5)
        wait.until(
            EC.visibility_of_element_located((By.ID, id))
        )
    except TimeoutException:
        logging.error(f"Time out alcanzado esperando al elemento con id '{id}'")

def clickar_boton_por_value(driver: webdriver.Chrome, value: str):
    try:
        wait = WebDriverWait(driver, 5)
        wait.until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, f"input[value='{value}']"))
        )
        boton = driver.find_element(By.CSS_SELECTOR, f"input[value='{value}']")
        boton.click()
        logging.info(f"Boton con value {value} clickado.")
    except TimeoutException:
        logging.error("Timed out")
    except Exception as e:
        logging.error(f"Falló clickando por value")

def clickar_boton_por_texto(driver: webdriver.Chrome, texto: str):
    try:
        wait = WebDriverWait(driver, 5)
        wait.until(
            EC.visibility_of_element_located((By.XPATH, f"//span[text()='{texto}']"))
        )
        boton = driver.find_element(By.XPATH, f"//span[text()='{texto}']")
        boton.click()
        logging.info(f"Boton con texto {texto} clickado.")
    except TimeoutException:
        logging.error("Time out al buscar por texto")
    except Exception as e:
        logging.error(f"Falló clickando por texto: '{e}'")