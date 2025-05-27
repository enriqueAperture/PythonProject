"""
Módulo: mainEmpresa.py

Este script automatiza el proceso de agregar empresas en la aplicación Nubelus.
El flujo de acciones es el siguiente:
  1. Configura el driver de Selenium y abre la web de Nubelus.
  2. Inicia sesión en Nubelus.
  3. Navega a la sección "Ficheros" y luego a "Entidades medioambientales".
  4. Interactúa con el pop-up para generar el Excel:
       - Clic en el ícono de opciones.
       - Clic en el botón para generar Excel.
       - Espera a que aparezca el pop-up y lo acepta.
  5. Vuelve al menú principal y obtiene las empresas no añadidas desde la información del Excel.
  6. Añade las empresas obtenidas mediante la función correspondiente.

Ejemplo de uso:
    Ejecuta este script para automatizar la adición de empresas en Nubelus.
"""

import time
import loggerConfig
import logging
import webConfiguration
import pandas
import excelFunctions
import webFunctions
import funcionesNubelus  # Módulo específico para la aplicación Nubelus


# URLs de la aplicación Nubelus
WEB_NUBELUS = "https://portal.nubelus.es"
WEB_NUBELUS_AÑADIR = "https://portal.nubelus.es/?clave=waster2_gestionEntidadesMedioambientales&pAccion=NUEVO"
WEB_NUBELUS_ACUERDOS = "https://portal.nubelus.es/?clave=waster2_gestionAcuerdosRepresentacion&pAccion=NUEVO"

# def añadir_empresa_medioambiental(driver):
#   """
#   Navega a la sección "Entidades medioambientales" y añade una empresa de prueba.
#   """
#   webFunctions.abrir_web(driver, WEB_NUBELUS_AÑADIR)
#   webFunctions.escribir_en_elemento_por_id(driver, "pDenominacion", "Empresa de Prueba")
#   webFunctions.escribir_en_elemento_por_name(driver, "pNif", "12345678A")
#   webFunctions.seleccionar_elemento_por_name(driver, "pForma_fiscal", "Física")
#   webFunctions.escribir_en_elemento_por_name(driver, "pNombre", "Nombre de Prueba")
#   webFunctions.escribir_en_elemento_por_name(driver, "pApellidos", "Apellido de Prueba")
#   webFunctions.escribir_en_elemento_por_name(driver, "pDomicilio", "Calle de Ejemplo 456")
#   webFunctions.completar_campo_y_confirmar_seleccion_por_name(driver, "pDenominacion_ine_municipio", "Valencia", "ui-a-label")
#   webFunctions.escribir_en_elemento_por_name(driver, "pPoblacion", "València/Valencia")
#   webFunctions.escribir_en_elemento_por_name(driver, "pCodigoPostal", "46003")
#   webFunctions.escribir_en_elemento_por_name(driver, "pTelefono", "912345678")
#   webFunctions.escribir_en_elemento_por_name(driver, "pEmail", "correo@electronico.com")
#   webFunctions.clickar_boton_por_clase(driver, "miBoton.aceptar")





def añadir_autorizaciones(driver):
  """
  Navega a la sección 'Autorizaciones' y añade una autorización de prueba.
  """
  webFunctions.seleccionar_elemento_por_id(driver, "fContenido_seleccionado", "Autorizaciones")
  time.sleep(1)
  webFunctions.clickar_boton_por_texto(driver, "Añadir autorización")

  oldDriver = driver
  popup = webFunctions.encontrar_pop_up_por_id(driver, "div_nuevo_AUTORIZACIONES")
  webFunctions.escribir_en_elemento_por_name(popup, "pAutorizacion_medioambiental", "Autorización de Prueba")
  webFunctions.escribir_en_elemento_por_name(popup, "pDenominacion", "Denominación de Prueba")
  webFunctions.escribir_en_elemento_por_name(popup, "pDenominacion_ema", "P04")
  time.sleep(1)
  webFunctions.clickar_boton_por_clase(driver, "BUSCAR_TIPO_ENTIDAD_MEDIOAMBIENTAL.noref.ui-menu-item")
  webFunctions.clickar_boton_por_clase(popup, "miBoton.aceptar")
  driver = oldDriver

def main():
  # Configurar el driver de Selenium
  driver = webConfiguration.configure()

  # Iniciar sesión en Nubelus
  funcionesNubelus.iniciar_sesion(driver)
  time.sleep(5)
  webFunctions.abrir_web(driver, WEB_NUBELUS_AÑADIR)
  excel_empresa = pandas.read_excel(excelFunctions.EXCEL_RECOGIDAS)
  excelFunctions.añadirEmpresa(driver, excel_empresa.iloc[0])
  #funcionesNubelus.crear_proveedor(driver)
  time.sleep(1)
  #funcionesNubelus.crear_cliente(driver)
  funcionesNubelus.entrar_en_centro_medioambiental(driver)
  excelFunctions.rellenar_datos_medioambientales(driver, excel_empresa.iloc[0])
  añadir_autorizaciones(driver)
  excelFunctions.añadir_horario(driver)
  excelFunctions.añadir_acuerdo_representacion(driver)

if __name__ == "__main__":
  main()
