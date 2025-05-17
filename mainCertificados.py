import time

import certHandler
import loggerConfig
import logging
import webConfiguration
import webFunctions

WEB_X = "https://x.com"
WEB_GOOGLE = "https://google.com"
NOMBRE_CERT = "RICARDO ESCUDE"

driver = webConfiguration.configure()

# Abrir Web
webFunctions.abrir_web(driver, WEB_GOOGLE)
webFunctions.escribir_en_elemento_por_class(driver, "gLFyf", "Estoy buscando en Google")
"""webFunctions.abrir_web(driver, WEB_MITECO)
webFunctions.esperar_elemento_por_id(driver, "breadcrumb")
webFunctions.clickar_boton_por_value(driver, "acceder")
webFunctions.clickar_boton_por_texto(driver, "Acceso DNIe / Certificado electrónico")"""
time.sleep(5)
#certHandler.seleccionar_certificado_chrome(NOMBRE_CERT)


