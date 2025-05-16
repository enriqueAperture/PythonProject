import os
import time

import pandas
import uiautomation as auto

import certHandler
import excelFunctions
import loggerConfig
import logging
import webConfiguration
import webFunctions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

WEB_NUBELUS = "https://portal.nubelus.es"
WEB_NUBELUS_EXCEL = "https://portal.nubelus.es/?clave=waster2_gestionEntidadesMedioambientales&pAccion=NUEVO"

driver = webConfiguration.configure()

# Abrir Web
webFunctions.abrir_web(driver, WEB_NUBELUS)
webFunctions.escribir_en_elemento_por_id(driver, "pNick_gestor", "ecotitan")
webFunctions.clickar_boton_por_id(driver, "btContinuar")
webFunctions.escribir_en_elemento_por_placeholder(driver, "Usuario", "dani")
webFunctions.escribir_en_elemento_por_placeholder(driver, "Contraseña", "123456")
webFunctions.clickar_boton_por_id(driver, "btAceptar")

time.sleep(5)
#webFunctions.abrir_web(driver, WEB_NUBELUS_EXCEL)

webFunctions.clickar_boton_por_link(driver, "Ficheros")
webFunctions.clickar_boton_por_link(driver, "Entidades medioambientales")

webFunctions.clickar_boton_por_clase(driver, "icon-ellipsis-vertical")
webFunctions.clickar_boton_por_id(driver, "moa_bGenerar_excel")
time.sleep(2)
webFunctions.esperar_elemento_por_id(driver, "div_relacion2excel")
webFunctions.aceptar_pop_up(driver, "div_relacion2excel", "miBoton.aceptar")

# Opcional: volver al contexto principal después de interactuar en el iframe
driver.switch_to.default_content()

webFunctions.clickar_boton_por_clase(driver, "navbar.superMenu")
empresas_añadir = excelFunctions.sacarEmpresasNoAñadidas(driver)
excelFunctions.añadirEmpresas(driver, empresas_añadir)




