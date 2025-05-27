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
import webFunctions
import funcionesNubelus  # Módulo específico para la aplicación Nubelus

# URLs de la aplicación Nubelus
WEB_NUBELUS = "https://portal.nubelus.es"
WEB_NUBELUS_AÑADIR = "https://portal.nubelus.es/?clave=waster2_gestionEntidadesMedioambientales&pAccion=NUEVO"
WEB_NUBELUS_ACUERDOS = "https://portal.nubelus.es/?clave=waster2_gestionAcuerdosRepresentacion&pAccion=NUEVO"

def añadir_empresa_medioambiental(driver):
  """
  Navega a la sección "Entidades medioambientales" y añade una empresa de prueba.
  """
  webFunctions.abrir_web(driver, WEB_NUBELUS_AÑADIR)
  webFunctions.escribir_en_elemento_por_id(driver, "pDenominacion", "Empresa de Prueba")
  webFunctions.escribir_en_elemento_por_name(driver, "pNif", "12345678A")
  webFunctions.seleccionar_elemento_por_name(driver, "pForma_fiscal", "Física")
  webFunctions.escribir_en_elemento_por_name(driver, "pNombre", "Nombre de Prueba")
  webFunctions.escribir_en_elemento_por_name(driver, "pApellidos", "Apellido de Prueba")
  webFunctions.escribir_en_elemento_por_name(driver, "pDomicilio", "Calle de Ejemplo 456")
  webFunctions.completar_campo_y_confirmar_seleccion_por_name(driver, "pDenominacion_ine_municipio", "Valencia", "ui-a-label")
  webFunctions.escribir_en_elemento_por_name(driver, "pPoblacion", "València/Valencia")
  webFunctions.escribir_en_elemento_por_name(driver, "pCodigoPostal", "46003")
  webFunctions.escribir_en_elemento_por_name(driver, "pTelefono", "912345678")
  webFunctions.escribir_en_elemento_por_name(driver, "pEmail", "correo@electronico.com")
  webFunctions.clickar_boton_por_clase(driver, "miBoton.aceptar")

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

def rellenar_datos_medioambientales(driver):
  """
  Rellena los datos medioambientales en el formulario correspondiente.
  """
  webFunctions.seleccionar_elemento_por_id(driver, "fContenido_seleccionado", "Datos medioambientales")
  time.sleep(1)
  webFunctions.clickar_boton_por_clase(driver, "miBoton.editar.solapa_descripcion")

  oldDriver = driver
  popup = webFunctions.encontrar_pop_up_por_id(driver, "div_editar_DATOS_MEDIOAMBIENTALES")
  webFunctions.escribir_en_elemento_por_name(popup, "pNima", "9876543210")
  webFunctions.escribir_en_elemento_por_name(popup, "pResponsable_ma_nombre", "Responsable de Prueba")
  webFunctions.escribir_en_elemento_por_name(popup, "pResponsable_ma_apellidos", "Apellido Responsable")
  webFunctions.escribir_en_elemento_por_name(popup, "pResponsable_ma_nif", "12345678A")
  webFunctions.escribir_en_elemento_por_name(popup, "pResponsable_ma_cargo", "Cargo de Prueba")
  webFunctions.completar_campo_y_confirmar_seleccion_por_name(driver, "pDenominacion_ine_vial", "Calle", "ui-a-label")
  webFunctions.escribir_en_elemento_por_name(popup, "pCodigo_cnae", "444444")
  webFunctions.escribir_en_elemento_por_name(popup, "pActividad_economica", "Actividad de Prueba")
  webFunctions.escribir_en_elemento_por_name(popup, "pCodigo_prtr", "123456")
  webFunctions.clickar_boton_por_clase(popup, "miBoton.aceptar")
  driver = oldDriver

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
  webFunctions.clickar_boton_por_clase(driver, "ui-a-label")
  webFunctions.clickar_boton_por_clase(popup, "miBoton.aceptar")
  driver = oldDriver

def añadir_horario(driver):
  """
  Navega a la sección 'Otros', abre el pop-up de aviso y añade un horario de prueba.
  """
  webFunctions.seleccionar_elemento_por_id(driver, "fContenido_seleccionado", "Otros")
  time.sleep(1)
  webFunctions.clickar_boton_con_titulo(driver, "Editar")
  oldDriver = driver
  popup = webFunctions.encontrar_pop_up_por_id(driver, "div_cambiar_aviso")
  webFunctions.escribir_en_elemento_por_name(popup, "pAviso", "Horario de Prueba")
  webFunctions.clickar_boton_por_clase(popup, "miBoton.aceptar")
  driver = oldDriver

def añadir_acuerdo_representacion(driver):
  """
  Navega a la sección de acuerdos de representación y añade un acuerdo de prueba.
  """
  webFunctions.abrir_web(driver, WEB_NUBELUS_ACUERDOS)
  time.sleep(1)
  webFunctions.completar_campo_y_confirmar_seleccion_por_name(driver, "pDenominacion_ema_representada", "Empresa de Prueba", "ui-a-label")
  webFunctions.escribir_en_elemento_por_name(driver, "pFecha", "01/01/2025")
  webFunctions.escribir_en_elemento_por_name(driver, "pFecha_caducidad", "02/01/2030")
  webFunctions.clickar_boton_por_clase(driver, "miBoton.aceptar")

def main():
  # Configurar el driver de Selenium
  driver = webConfiguration.configure()

  # Iniciar sesión en Nubelus
  funcionesNubelus.iniciar_sesion(driver)
  time.sleep(5)
  añadir_empresa_medioambiental(driver)
  crear_proveedor(driver)
  time.sleep(1)
  crear_cliente(driver)
  entrar_en_centro_medioambiental(driver)
  rellenar_datos_medioambientales(driver)
  añadir_autorizaciones(driver)
  añadir_horario(driver)
  añadir_acuerdo_representacion(driver)

if __name__ == "__main__":
  main()
