import time

import certHandler
import loggerConfig
import logging
import webConfiguration
import webFunctions

WEB_NUBELUS = "https://portal.nubelus.es"

driver = webConfiguration.configure()

# Abrir Web
webFunctions.abrir_web(driver, WEB_NUBELUS)
webFunctions.escribir_en_elemento_por_id(driver, "pNick_gestor", "ecotitan")
webFunctions.clickar_boton_por_id(driver, "btContinuar")
webFunctions.escribir_en_elemento_por_placeholder(driver, "Usuario", "dani")
webFunctions.escribir_en_elemento_por_placeholder(driver, "Contraseña", "123456")
webFunctions.clickar_boton_por_id(driver, "btAceptar")
webFunctions.aceptarAlerta(driver)




