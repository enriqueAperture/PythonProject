import shutil
import time

from selenium.webdriver.common.by import By

import certHandler
import loggerConfig
import logging
import webConfiguration
import webFunctions

WEB_NIMA_VLC = "https://residuos.gva.es/RES_BUSCAWEB/buscador_residuos_avanzado.aspx"
NIF = "B43693274"

driver = webConfiguration.configure()

# Abrir Web
webFunctions.abrir_web(driver, WEB_NIMA_VLC)
webFunctions.escribir_en_elemento_por_id(driver, "ctl00_ContentPlaceHolder1_txtNIF", NIF)
webFunctions.clickar_boton_por_id(driver, "ctl00_ContentPlaceHolder1_btBuscar")
webFunctions.abrir_link_por_boton_id(driver, "ctl00_ContentPlaceHolder1_gvResultados_ctl03_hypGestor")
documento = driver.find_element(By.ID, "bobjid_1747726678906")
html_interno = documento.get_attribute("innerHTML")
print(html_interno)
logging.info(documento.find_element(By.CLASS_NAME, "fc42991094-4e71-4327-ba9c-3c93a93d0e8b-2").text)
