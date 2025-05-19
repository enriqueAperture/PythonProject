import shutil
import time

import certHandler
import loggerConfig
import logging
import webConfiguration
import webFunctions

WEB_MITECO = "https://sede.miteco.gob.es/portal/site/seMITECO/login"
WEB_GOOGLE = "https://google.com"
NOMBRE_CERT = "RICARDO ESCUDE"

driver = webConfiguration.configure()

# Abrir Web
webFunctions.abrir_web(driver, WEB_MITECO)
webFunctions.esperar_elemento_por_id(driver, "breadcrumb")
webFunctions.clickar_boton_por_value(driver, "acceder")
webFunctions.clickar_boton_por_texto(driver, "Acceso DNIe / Certificado electrónico")
certHandler.seleccionar_certificado_chrome(NOMBRE_CERT)
time.sleep(30)
driver.quit()


