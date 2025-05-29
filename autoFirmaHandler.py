"""
Módulo: autoFirmaHandler.py

Este módulo contiene funciones para la automatización del proceso de firma mediante AutoFirma,
utilizando la librería uiautomation junto con funciones auxiliares de uiautomationHandler para:
 
  - Imprimir los títulos de las ventanas abiertas.
  - Obtener recursivamente todos los controles de tipo RadioButton.
  - Seleccionar un certificado que contenga una subcadena específica y confirmar la selección 
    haciendo clic en el botón "Aceptar" del popup "Diálogo de seguridad de almacén Windows".
  - Administrar el flujo del proceso de firma en AutoFirma, incluyendo la interacción con el popup
    "¿Abrir AutoFirma?".

Ejemplos de uso:

    # Para seleccionar un certificado y confirmar en AutoFirma:
    if seleccionar_certificado(ventana_cert, "FRANCISCO JAVIER"):
        logging.info("Certificado seleccionado y confirmado correctamente.")
    else:
        logging.error("No se pudo seleccionar el certificado.")

    # Para iniciar el proceso de firma a través de AutoFirma:
    firmar_en_autofirma()
"""

import logging
import time
import loggerConfig
import uiautomation
import uiautomationHandler

def print_open_windows_titles():
    """
    Imprime el título de todas las ventanas abiertas en el sistema.

    Recorre las ventanas hijas del control raíz de uiautomation y escribe el título de cada una.

    Ejemplo de uso:
        print_open_windows_titles()
    """
    for w in uiautomation.GetRootControl().GetChildren():
        logging.warning(f'Window: {w.Name}')

def _obtener_radio_buttons(control):
    """
    Recorre recursivamente un control y devuelve todos los controles de tipo RadioButton.

    Args:
        control: Control en el cual se realizará la búsqueda de RadioButton.

    Returns:
        list: Lista de controles de tipo RadioButton encontrados.

    Ejemplo de uso:
        radios = _obtener_radio_buttons(ventana_cert)
    """
    radios = []
    for child in control.GetChildren():
        if child.ControlTypeName == 'RadioButton':
            radios.append(child)
        else:
            radios.extend(_obtener_radio_buttons(child))
    return radios

def seleccionar_certificado(ventana_cert, nombre_certificado="FRANCISCO JAVIER"):
    """
    Selecciona el certificado que contenga la subcadena especificada en el parámetro nombre_certificado,
    utilizando los controles DataItemControl obtenidos mediante uiautomationHandler, y hace clic en 
    el botón "Aceptar" del popup "Diálogo de seguridad de almacén Windows".

    Args:
        ventana_cert: Control de la ventana de certificados.
        nombre_certificado (str, optional): Subcadena que debe contener el nombre del certificado. 
                                              Por defecto "FRANCISCO JAVIER".

    Returns:
        bool: True si se pudo seleccionar el certificado y se hizo clic en "Aceptar"; False en caso contrario.

    Ejemplo de uso:
        if seleccionar_certificado(ventana_cert, "FRANCISCO JAVIER"):
            logging.info("Certificado seleccionado y confirmado correctamente.")
        else:
            logging.error("No se pudo seleccionar el certificado.")
    """
    if not ventana_cert:
        logging.error("No se encontró la ventana de certificado.")
        return False

    # Obtener todos los controles tipo DataItemControl (se asume que representan los certificados)
    certificados = uiautomationHandler.obtener_data_item_control(ventana_cert)
    if not certificados:
        logging.error("No se encontraron controles de certificado.")
        return False

    # Buscar en la lista el certificado que contenga el nombre deseado
    certificado_encontrado = None
    for cert in certificados:
        time.sleep(0.5)  # Breve pausa para mayor estabilidad
        if nombre_certificado in cert.Name:
            certificado_encontrado = cert
            break

    if certificado_encontrado:
        logging.info(f"Certificado encontrado: {certificado_encontrado.Name}. Seleccionándolo...")
        certificado_encontrado.Click()
    else:
        logging.error(f"No se encontró un certificado que contenga '{nombre_certificado}'.")
        return False

    # Una vez seleccionado, se hace clic en el botón "Aceptar" en el popup 
    # "Diálogo de seguridad de almacén Windows" mediante uiautomationHandler.click_boton.
    if uiautomationHandler.click_boton(ventana_cert, "Diálogo de seguridad de almacén Windows", "Aceptar", timeout=5):
        logging.info("Se hizo clic en el botón 'Aceptar'.")
        return True
    else:
        logging.error("No se pudo hacer clic en el botón 'Aceptar'.")
        return False

def firmar_en_autofirma():
    """
    Inicia el proceso de firma en AutoFirma.

    Utiliza uiautomationHandler para:
      1. Obtener la ventana de Chrome.
      2. Esperar y hacer clic en el popup "¿Abrir AutoFirma?" mediante un callback.
      3. Listar las ventanas abiertas para diagnóstico.
      4. Esperar y ejecutar la selección del certificado a través del popup "Diálogo de seguridad del almacén Windows".
      5. Finalmente, vuelve a intentar la selección del certificado para continuar el proceso de firma.

    Ejemplo de uso:
        firmar_en_autofirma()
    """
    ventana_chrome = uiautomationHandler.obtener_ventana_chrome()
    # Esperar el popup "¿Abrir AutoFirma?" y hacer clic en el botón "Abrir AutoFirma"
    uiautomationHandler.esperar_popup_y_ejecutar(
        ventana_chrome,
        "¿Abrir AutoFirma?",
        accion=lambda popup: uiautomationHandler.click_boton(ventana_chrome, "¿Abrir AutoFirma?", "Abrir AutoFirma"),
        timeout=10
    )
    time.sleep(5)
    # Imprimir títulos de las ventanas abiertas para depuración
    print_open_windows_titles()
    # Esperar el popup "Diálogo de seguridad del almacén Windows" y ejecutar la selección de certificado
    uiautomationHandler.esperar_popup_y_ejecutar(
        ventana_chrome,
        "Diálogo de seguridad del almacén Windows",
        accion=lambda popup: seleccionar_certificado(ventana_chrome),
        timeout=10
    )
