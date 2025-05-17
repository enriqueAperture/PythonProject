"""
Módulo: funcionesNubelus.py

Este módulo contiene funciones específicas para la aplicación Nubelus, utilizando Selenium WebDriver.
Actualmente, proporciona una función para iniciar sesión en la plataforma Nubelus.

Funciones:
    - iniciar_sesion(driver): Abre la web de Nubelus y realiza las acciones necesarias para iniciar sesión.
    
Ejemplo de uso:
    from selenium import webdriver
    import funcionesNubelus
    driver = webdriver.Chrome()
    funcionesNubelus.iniciar_sesion(driver)
"""

import webFunctions

# URL de la web de Nubelus
WEB_NUBELUS = "https://portal.nubelus.es"

def iniciar_sesion(driver):
    """
    Inicia sesión en la plataforma Nubelus utilizando el driver de Selenium.
    
    La función realiza las siguientes acciones:
      1. Abre la web de Nubelus.
      2. Escribe en el campo con id "pNick_gestor" el valor "ecotitan".
      3. Hace clic en el botón con id "btContinuar".
      4. Escribe en el campo con placeholder "Usuario" el valor "dani".
      5. Escribe en el campo con placeholder "Contraseña" el valor "123456".
      6. Hace clic en el botón con id "btAceptar".
    
    Args:
        driver (webdriver.Chrome): Instancia del navegador Selenium.
    
    Ejemplo:
        iniciar_sesion(driver)
    """
    webFunctions.abrir_web(driver, WEB_NUBELUS)
    webFunctions.escribir_en_elemento_por_id(driver, "pNick_gestor", "ecotitan")
    webFunctions.clickar_boton_por_id(driver, "btContinuar")
    webFunctions.escribir_en_elemento_por_placeholder(driver, "Usuario", "dani")
    webFunctions.escribir_en_elemento_por_placeholder(driver, "Contraseña", "123456")
    webFunctions.clickar_boton_por_id(driver, "btAceptar")