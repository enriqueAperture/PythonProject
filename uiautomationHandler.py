import loggerConfig
import uiautomation as auto
import time
import logging

def obtener_ventana_chrome(timeout=10):
    """Busca y activa la ventana de Google Chrome."""
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
        ventana_chrome: Control de la ventana de Chrome.
        popup_name (str): Nombre del popup a buscar.
        button_name (str): Nombre del botón a clickar dentro del popup.
        timeout (int, optional): Tiempo máximo de espera en segundos. Por defecto 5.

    Returns:
        bool: True si se encontró y se hizo click en el botón; False en caso contrario.

    Ejemplos de uso:
        # Para hacer click en "Abrir AutoFirma" en un popup llamado "¿Abrir AutoFirma?"
        click_boton(ventana_chrome, "¿Abrir AutoFirma?", "Abrir AutoFirma", timeout=5)

        # Para hacer click en "Aceptar" en un popup llamado "Seleccionar un certificado"
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
    Espera a que se muestre un popup (definido por su Name) en la ventana de Chrome y,
    si se encuentra, ejecuta la función 'accion' pasándole el control del popup.
    
    Args:
        ventana_chrome: Control de la ventana Chrome obtenido por uiautomation.
        popup_name (str): Nombre del popup a esperar.
        accion (callable, optional): Función que se ejecutará pasando el popup como argumento.
                                     Si no se proporciona, se devuelve el popup.
        timeout (int, optional): Tiempo máximo de espera en segundos. Por defecto 10.
    
    Returns:
        Si se define 'accion': devuelve el resultado de la acción.
        Si no se define 'accion': devuelve el control del popup.
        En caso de error (no se encuentra el popup) se devuelve None.
        
    Ejemplos:
        # Caso 1: En autoFirmaHandler para hacer click en "Abrir AutoFirma":
        _esperar_popup_y_ejecutar(ventana_chrome, "¿Abrir AutoFirma?", 
            accion=lambda popup: uiautomationHandler.click_boton(ventana_chrome, "¿Abrir AutoFirma?", "Abrir AutoFirma"), 
            timeout=10)
        
        # Caso 2: En certHandler para obtener la lista de certificados:
        certificados = _esperar_popup_y_ejecutar(ventana_chrome, "Seleccionar un certificado", 
            accion=lambda popup: _obtener_data_item_control(popup), 
            timeout=10)
    """
    logging.info(f"Esperando popup '{popup_name}'...")
    popup_cert = None
    start_time = time.time()
    while not popup_cert and (time.time() - start_time) < timeout:
        popup_cert = ventana_chrome.Control(searchDepth=20, ControlType=auto.ControlType.CustomControl, Name=popup_name)
        if not popup_cert.Exists():
            popup_cert = None
            time.sleep(0.5)
    if popup_cert:
        logging.info(f"Popup '{popup_name}' detectado.")
        if accion is not None:
            return accion(popup_cert)
        else:
            return popup_cert
    else:
        logging.error(f"No se encontró el popup '{popup_name}'.")
        return None