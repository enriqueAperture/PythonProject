"""
Módulo: uiautomationHandler.py

Este módulo contiene funciones auxiliares para la interacción con la interfaz 
de usuario mediante la librería uiautomation. Entre las funcionalidades se incluyen:

  - obtener_ventana_chrome(timeout=10):
      Busca y activa la ventana de Google Chrome basada en su clase y nombre.

  - click_boton(ventana_chrome, popup_name, button_name, timeout=5):
      Busca y hace clic en un botón específico dentro de un popup de la ventana proporcionada.

  - esperar_popup_y_ejecutar(ventana_chrome, popup_name, accion=None, timeout=10):
      Espera a que se muestre un popup (identificado por su Name) y, si se define una acción,
      la ejecuta pasando el control del popup; en caso contrario, devuelve el control del popup.

  - obtener_data_item_control(control):
      Busca recursivamente todos los controles de tipo DataItemControl dentro de un control.

Ejemplos de uso:

    # Buscar la ventana de Chrome
    ventana = obtener_ventana_chrome(timeout=10)

    # Hacer clic en un botón "Abrir AutoFirma" dentro de un popup llamado "¿Abrir AutoFirma?"
    click_boton(ventana, "¿Abrir AutoFirma?", "Abrir AutoFirma", timeout=5)

    # Esperar a que aparezca el popup "Seleccionar un certificado" y obtener los controles DataItemControl
    certificados = esperar_popup_y_ejecutar(ventana, "Seleccionar un certificado", 
                     accion=lambda popup: obtener_data_item_control(popup), timeout=10)
"""

import loggerConfig
import uiautomation as auto
import time
import logging

def obtener_ventana_chrome(timeout=10):
    """
    Busca y activa la ventana de Google Chrome.

    Args:
        timeout (int, optional): Tiempo máximo de espera en segundos. Por defecto 10.

    Returns:
        Control: El control de la ventana de Chrome encontrada o None si no se encuentra.

    Ejemplo de uso:
        ventana = obtener_ventana_chrome(timeout=10)
    """
    logging.info("Buscando ventana de Chrome...")
    ventana_chrome = None
    start_time = time.time()
    while not ventana_chrome and (time.time() - start_time) < timeout:
        for w in auto.GetRootControl().GetChildren():
            if w.ClassName == 'Chrome_WidgetWin_1' and 'Chrome' in w.Name:
                ventana_chrome = w
                break
        time.sleep(0.5)

    if ventana_chrome:
        logging.info(f"Ventana de Chrome encontrada: {ventana_chrome.Name}")
        ventana_chrome.SetActive()
        return ventana_chrome
    else:
        logging.error("No se encontró la ventana de Chrome.")
        return None

def click_boton(ventana_chrome, popup_name: str, button_name: str, timeout: int = 5) -> bool:
    """
    Busca y hace clic en un botón específico dentro de un popup dado.

    Args:
        ventana_chrome: Control de la ventana sobre la cual se buscará el popup.
        popup_name (str): Nombre del popup a buscar.
        button_name (str): Nombre del botón a clickar dentro del popup.
        timeout (int, optional): Tiempo máximo de espera en segundos. Por defecto 5.

    Returns:
        bool: True si se encontró y se hizo clic en el botón; False en caso contrario.

    Ejemplos de uso:
        click_boton(ventana_chrome, "¿Abrir AutoFirma?", "Abrir AutoFirma", timeout=5)
        click_boton(ventana_chrome, "Seleccionar un certificado", "Aceptar", timeout=5)
    """
    logging.info(f"Buscando botón '{button_name}' en popup '{popup_name}'...")
    popup_cert = ventana_chrome.Control(
        searchDepth=20,
        ControlType=auto.ControlType.CustomControl,
        Name=popup_name
    )
    if popup_cert.Exists(maxSearchSeconds=timeout):
        boton = popup_cert.ButtonControl(Name=button_name)
        if boton.Exists(maxSearchSeconds=timeout):
            logging.info(f"¡Botón '{button_name}' encontrado! Haciendo click...")
            boton.Click()
            return True
        else:
            logging.error(f"No se encontró el botón '{button_name}' en el popup '{popup_name}'.")
            return False
    else:
        logging.error(f"No se encontró el popup '{popup_name}' para buscar el botón '{button_name}'.")
        return False

def esperar_popup_y_ejecutar(ventana_chrome, popup_name: str, accion: callable = None, timeout: int = 10):
    """
    Espera a que se muestre un popup (definido por su Name) en la ventana y,
    si se encuentra, ejecuta la función 'accion' pasándole el control del popup.

    Args:
        ventana_chrome: Control de la ventana obtenido por uiautomation.
        popup_name (str): Nombre del popup a esperar.
        accion (callable, optional): Función que se ejecutará pasando el popup como argumento.
                                     Si no se proporciona, se devuelve el control del popup.
        timeout (int, optional): Tiempo máximo de espera en segundos. Por defecto 10.

    Returns:
        Si se define 'accion': devuelve el resultado de la acción.
        Si no se define 'accion': devuelve el control del popup.
        En caso de error (no se encuentra el popup) se devuelve None.

    Ejemplos de uso:
        # Caso 1: Hacer click en "Abrir AutoFirma" en un popup llamado "¿Abrir AutoFirma?"
        esperar_popup_y_ejecutar(ventana_chrome, "¿Abrir AutoFirma?",
            accion=lambda popup: click_boton(ventana_chrome, "¿Abrir AutoFirma?", "Abrir AutoFirma", timeout=5),
            timeout=10)
        
        # Caso 2: Obtener la lista de controles DataItemControl en el popup "Seleccionar un certificado"
        certificados = esperar_popup_y_ejecutar(ventana_chrome, "Seleccionar un certificado",
            accion=lambda popup: obtener_data_item_control(popup), timeout=10)
    """
    logging.info(f"Esperando popup '{popup_name}'...")
    popup_cert = None
    start_time = time.time()
    while not popup_cert and (time.time() - start_time) < timeout:
        popup_cert = ventana_chrome.Control(
            searchDepth=20,
            ControlType=auto.ControlType.CustomControl,
            Name=popup_name
        )
        if not popup_cert.Exists():
            popup_cert = None
            time.sleep(0.5)
    if popup_cert:
        logging.info(f"Popup '{popup_name}' detectado.")
        # Se pasa el control del popup a la acción o se devuelve el popup
        if accion is not None:
            return accion(popup_cert)
        else:
            return popup_cert
    else:
        logging.error(f"No se encontró el popup '{popup_name}'.")
        return None

def obtener_data_item_control(control):
    """
    Busca recursivamente controles de tipo DataItemControl dentro de un control.

    Args:
        control: Control en el cual se realizará la búsqueda.

    Returns:
        list: Una lista de controles de tipo DataItemControl encontrados dentro de 'control'.

    Ejemplo de uso:
        data_items = obtener_data_item_control(control_principal)
    """
    data_items = []
    for child in control.GetChildren():
        if child.ControlTypeName == 'DataItemControl':
            data_items.append(child)
        else:
            # Si no es DataItemControl, se realiza una búsqueda recursiva en sus hijos
            data_items.extend(obtener_data_item_control(child))
    return data_items
