"""
Módulo: mainCertificados.py

Este módulo orquesta el flujo de automatización para la gestión de certificados en la web de MITECO,
utilizando Selenium para interactuar con la interfaz web y uiautomation junto con funciones auxiliares
de autoFirmaHandler y certHandler para la selección del certificado a utilizar (por DNIe o certificado electrónico).

Flujo general:
  1. Configura el driver de Selenium y abre la URL correspondiente a la web de MITECO.
  2. Espera y verifica la carga inicial de la web (por ejemplo, mediante la presencia de un elemento identificador).
  3. Realiza acciones de navegación e interacción:
     - Acceso mediante botón ("acceder").
     - Selección del método de acceso ("Acceso DNIe / Certificado electrónico").
  4. Llama a la función del módulo certHandler para seleccionar el certificado deseado.
  5. Completa un formulario rellenando campos como dirección, país, provincia, municipio, código postal, teléfono, etc.
  6. Realiza la subida de un archivo XML y posteriormente finaliza el proceso mediante las llamadas a funciones
     encargadas de la firma (autoFirmaHandler).
  7. Finalmente, cierra el driver.

Ejemplo de uso:
    Ejecutar este script inicia el flujo de automatización para el proceso de certificados en MITECO.
    Al finalizar, se cierra el navegador.
"""

import os
import time
import autoFirmaHandler
import certHandler
from config import BASE_DIR
import loggerConfig
import logging
import webConfiguration
import webFunctions

# URL y configuraciones
WEB_MITECO = ("https://sede.miteco.gob.es/portal/site/seMITECO/login?"
              "urlLoginRedirect=L3BvcnRhbC9zaXRlL3NlTUlURUNPL3BvcnRsZXRfYnVzP2lkX3Byb2NlZGltaWVudG89NzM2"
              "JmlkZW50aWZpY2Fkb3JfcGFzbz1QUkVJTklDSU8mc3ViX29yZ2Fubz0xMSZwcmV2aW9fbG9naW49MQ==")
NOMBRE_CERT = "FRANCISCO"
ARCHIVO_XML = os.path.join(BASE_DIR, "data", "NT30460004811420250009974.xml")

# Configurar el driver de Selenium
driver = webConfiguration.configure()

# Abrir la web de MITECO
webFunctions.abrir_web(driver, WEB_MITECO)
webFunctions.esperar_elemento_por_id(driver, "breadcrumb")

# Proceso de autenticación y selección de acceso
webFunctions.clickar_boton_por_value(driver, "acceder")
webFunctions.clickar_boton_por_texto(driver, "Acceso DNIe / Certificado electrónico")

# Selección del certificado (utiliza certHandler para buscar y confirmar el certificado deseado)
certHandler.seleccionar_certificado_chrome(NOMBRE_CERT)

# Espera a que la página principal del formulario cargue
webFunctions.esperar_elemento_por_id(driver, "wrapper", timeout=15)

# Rellenar los datos del formulario
webFunctions.escribir_en_elemento_por_id(driver, "id_direccion", "Direccion")
webFunctions.seleccionar_elemento_por_id(driver, "id_pais", "España")
webFunctions.seleccionar_elemento_por_id(driver, "id_provincia", "València/Valencia")
webFunctions.seleccionar_elemento_por_id(driver, "id_municipio", "Aldaia")
webFunctions.escribir_en_elemento_por_id(driver, "id_codigo_postal", "46003")
webFunctions.escribir_en_elemento_por_id(driver, "id_telefono", "912345678")
webFunctions.escribir_en_elemento_por_id(driver, "id_telefono_movil", "612345678")
webFunctions.escribir_en_elemento_por_id(driver, "id_correo_electronico", "correo@electronico.com")
webFunctions.escribir_en_elemento_por_id(driver, "id_fax", "012345678")

# Enviar el formulario
webFunctions.clickar_boton_por_id(driver, "btnForm")
time.sleep(5)

# Seleccionar el método de envío de datos
webFunctions.clickar_boton_por_id(driver, "tipoEnvioNtA")
webFunctions.escribir_en_elemento_por_id(driver, "file", ARCHIVO_XML)

# Continuar con el proceso de autenticación y firma
webFunctions.clickar_boton_por_clase(driver, "loginBtn")
webFunctions.clickar_boton_por_texto(driver, "Continuar")
webFunctions.clickar_boton_por_id(driver, "bSiguiente")
webFunctions.clickar_boton_por_id(driver, "idFirmarRegistrar")
time.sleep(3)
webFunctions.clickar_boton_por_id(driver, "idFirmarRegistrar")

# Ejecutar el proceso de firma mediante AutoFirma
autoFirmaHandler.firmar_en_autofirma()

# Cerrar el navegador
driver.quit()
