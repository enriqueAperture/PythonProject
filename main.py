import time

import certHandler
import loggerConfig
import logging
import webConfiguration
import webFunctions

WEB_MITECO = "https://sede.miteco.gob.es/portal/site/seMITECO/portlet_bus?id_procedimiento=736&identificador_paso=PREINICIO&sub_organo=11&previo_login=1"
NOMBRE_CERT = "RICARDO ESCUDE"
NOMBRE_CERT = ""

driver = webConfiguration.configure()

# Abrir Web
webFunctions.abrir_web(driver, WEB_MITECO)
webFunctions.esperar_elemento_por_id(driver, "breadcrumb")
webFunctions.clickar_boton_por_value(driver, "acceder")
webFunctions.clickar_boton_por_texto(driver, "Acceso DNIe / Certificado electrónico")
time.sleep(5)
#certHandler.seleccionar_certificado_chrome(NOMBRE_CERT)


