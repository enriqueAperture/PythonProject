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
import time

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

def crear_proveedor(driver):
  """
  Hace clic en 'Crear proveedor' y acepta el pop-up correspondiente.
  """
  webFunctions.clickar_boton_por_texto(driver, "Crear proveedor")
  oldDriver = driver
  popup = webFunctions.encontrar_pop_up_por_id(driver, "div_crear_proveedor")
  webFunctions.clickar_boton_por_clase(popup, "miBoton_cuadrado.aceptar")
  driver = oldDriver

def crear_cliente(driver):
  """
  Hace clic en 'Crear cliente' y acepta el pop-up correspondiente.
  """
  webFunctions.clickar_boton_por_texto(driver, "Crear cliente")
  oldDriver = driver
  popup = webFunctions.encontrar_pop_up_por_id(driver, "div_crear_cliente")
  webFunctions.clickar_boton_por_clase(popup, "miBoton_cuadrado.aceptar")
  driver = oldDriver

def entrar_en_centro_medioambiental(driver):
  """
  Accede a la sección 'Centros' dentro del área medioambiental y selecciona un registro.
  """
  webFunctions.seleccionar_elemento_por_id(driver, "fContenido_seleccionado", "Centros")
  time.sleep(1)
  webFunctions.clickar_boton_por_clase(driver, "registro")