import shutil
import time

from selenium.webdriver.common.by import By

import autoFirmaHandler
import certHandler
import loggerConfig
import logging
import webConfiguration
import webFunctions

WEB_MITECO = "https://sede.miteco.gob.es/portal/site/seMITECO/login?urlLoginRedirect=L3BvcnRhbC9zaXRlL3NlTUlURUNPL3BvcnRsZXRfYnVzP2lkX3Byb2NlZGltaWVudG89NzM2JmlkZW50aWZpY2Fkb3JfcGFzbz1QUkVJTklDSU8mc3ViX29yZ2Fubz0xMSZwcmV2aW9fbG9naW49MQ=="
NOMBRE_CERT = "FRANCISCO"
ARCHIVO_XML = "C:/Users/USUARIO/Documents/GitHub/PythonProject/data/NT30460004811420250009971.xml"

def print_open_windows_titles():
    """
    Imprime el título de todas las ventanas abiertas del ordenador.
    """
    root = auto.GetRootControl()
    windows = root.GetChildren()
    for win in windows:
        # Verificar que es una ventana y tiene un título
        if win.ControlTypeName == 'Window':
            title = win.Name or '(Sin título)'
            print(f'Window: {title}')

driver = webConfiguration.configure()

# Abrir Web
webFunctions.abrir_web(driver, WEB_MITECO)
webFunctions.esperar_elemento_por_id(driver, "breadcrumb")
webFunctions.clickar_boton_por_value(driver, "acceder")
webFunctions.clickar_boton_por_texto(driver, "Acceso DNIe / Certificado electrónico")
certHandler.seleccionar_certificado_chrome(NOMBRE_CERT)
webFunctions.esperar_elemento_por_id(driver, "wrapper", timeout=15)
webFunctions.escribir_en_elemento_por_id(driver, "id_direccion", "Direccion")
webFunctions.seleccionar_elemento_por_id(driver, "id_pais", "España")
webFunctions.seleccionar_elemento_por_id(driver, "id_provincia", "València/Valencia")
webFunctions.seleccionar_elemento_por_id(driver, "id_municipio", "Aldaia")
webFunctions.escribir_en_elemento_por_id(driver, "id_codigo_postal", "46003")
webFunctions.escribir_en_elemento_por_id(driver, "id_telefono", "912345678")
webFunctions.escribir_en_elemento_por_id(driver, "id_telefono_movil", "612345678")
webFunctions.escribir_en_elemento_por_id(driver, "id_correo_electronico", "correo@electronico.com")
webFunctions.escribir_en_elemento_por_id(driver, "id_fax", "012345678")
webFunctions.clickar_boton_por_id(driver, "btnForm")
time.sleep(5)
webFunctions.clickar_boton_por_id(driver, "tipoEnvioNtA")
webFunctions.escribir_en_elemento_por_id(driver, "file", ARCHIVO_XML)
webFunctions.clickar_boton_por_clase(driver, "loginBtn")
webFunctions.clickar_boton_por_texto(driver, "Continuar")
webFunctions.clickar_boton_por_id(driver, "bSiguiente")
webFunctions.clickar_boton_por_id(driver, "idFirmarRegistrar")
autoFirmaHandler.firmar_en_AutoFirma()
print_open_windows_titles()
time.sleep(3600)

driver.quit()


