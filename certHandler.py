import loggerConfig
import uiautomation as auto
import time
import logging

def _obtener_ventana_chrome(timeout=10):
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

def _obtener_data_item_control(control):
    """Busca recursivamente controles de tipo DataItemControl dentro de un control."""
    data_items = []
    for child in control.GetChildren():
        if child.ControlTypeName == 'DataItemControl':
            data_items.append(child)
        else:
            # Si no es DataItemControl, busca recursivamente en sus hijos
            data_items.extend(_obtener_data_item_control(child))
    return data_items

def _obtener_lista_certificados(ventana_chrome, timeout=10):
    """Espera y obtiene los controles DataItemControl de forma recursiva."""
    logging.info("Esperando popup de certificado...")
    popup_cert = None
    start_time = time.time()
    while not popup_cert and (time.time() - start_time) < timeout:
        popup_cert = ventana_chrome.Control(searchDepth=20, ControlType=auto.ControlType.CustomControl,
                                            Name='Seleccionar un certificado')
        if not popup_cert.Exists():
            popup_cert = None
            time.sleep(0.5)

    if popup_cert:
        logging.info("Popup de certificado detectado.")
        certificados = _obtener_data_item_control(popup_cert)
        nombres_certificados = [cert.Name for cert in certificados]
        logging.info(f"Nombres de certificados encontrados: {nombres_certificados}")
        return certificados
    else:
        logging.error("No se encontró el popup de certificado.")
        return []

def _obtener_pop_up_autofirma(ventana_chrome, timeout=10):
    """Espera y obtiene los controles DataItemControl de forma recursiva."""
    logging.info("Esperando popup de certificado...")
    popup_cert = None
    start_time = time.time()
    while not popup_cert and (time.time() - start_time) < timeout:
        popup_cert = ventana_chrome.Control(searchDepth=20, ControlType=auto.ControlType.CustomControl,
                                            Name='¿Abrir AutoFirma?')
        if not popup_cert.Exists():
            popup_cert = None
            time.sleep(0.5)

    if popup_cert:
        logging.info("Popup de autofirma detectado.")
        _click_boton_abrir(popup_cert)
        return certificados
    else:
        logging.error("No se encontró el popup de certificado.")
        return []

def _click_boton_abrir(ventana_chrome, name: str = '¿Abrir AutoFirma?', timeout=5):
    """Busca y hace clic en el botón 'Aceptar' en el popup de certificado."""
    logging.info("Buscando botón 'Abrir AutoFirma'...")
    popup_cert = ventana_chrome.Control(searchDepth=20, ControlType=auto.ControlType.CustomControl, Name=name)
    if popup_cert.Exists(maxSearchSeconds=timeout):
        boton_aceptar = popup_cert.ButtonControl(Name='Abrir AutoFirma')
        if boton_aceptar.Exists(maxSearchSeconds=timeout):
            logging.info("¡Botón 'Abrir AutoFirma' encontrado! Haciendo click...")
            boton_aceptar.Click()
            return True
        else:
            logging.error("No se encontró el botón 'Abrir AutoFirma' en el popup de certificado.")
            return False
    else:
        logging.error("No se encontró el popup de certificado para buscar el botón 'Abrir AutoFirma'.")
        return False

def _seleccionar_certificado(lista_certificados, nombre_certificado):
    """Selecciona el certificado deseado de la lista."""
    cert_encontrado = None
    found = False

    for certificado in lista_certificados:
        time.sleep(1)
        if nombre_certificado in certificado.Name:
            cert_encontrado = certificado
            break

    if cert_encontrado:
        logging.info(f"Certificado encontrado con nombre: {cert_encontrado.Name}")
        logging.info(f"Intentando hacer clic en el certificado: {cert_encontrado.Name}")
        cert_encontrado.Click()
        found = True
    else:
        logging.error(f"No hay certificados con el nombre '{nombre_certificado}'.")

    return found

def _click_boton_aceptar(ventana_chrome, name: str = 'Seleccionar un certificado', timeout=5):
    """Busca y hace clic en el botón 'Aceptar' en el popup de certificado."""
    logging.info("Buscando botón 'Aceptar'...")
    popup_cert = ventana_chrome.Control(searchDepth=20, ControlType=auto.ControlType.CustomControl, Name=name)
    if popup_cert.Exists(maxSearchSeconds=timeout):
        boton_aceptar = popup_cert.ButtonControl(Name='Aceptar')
        if boton_aceptar.Exists(maxSearchSeconds=timeout):
            logging.info("¡Botón 'Aceptar' encontrado! Haciendo click...")
            boton_aceptar.Click()
            return True
        else:
            logging.error("No se encontró el botón 'Aceptar' en el popup de certificado.")
            return False
    else:
        logging.error("No se encontró el popup de certificado para buscar el botón 'Aceptar'.")
        return False

def seleccionar_certificado_chrome(nombre_certificado='RICARDO ESCUDE'):
    """Función principal para llegar a la ventana de Chrome, obtener los certificados
    y seleccionar el certificado especificado."""
    ventana_chrome = _obtener_ventana_chrome()
    if not ventana_chrome:
        return False

    # Usar la versión modificada de _obtener_lista_certificados
    lista_certificados = _obtener_lista_certificados(ventana_chrome)
    if lista_certificados is []:
        logging.warning("La lista de certificados está vacía.")
        return False

    logging.info(f"Primer certificado encontrado: {lista_certificados[0].Name if lista_certificados else 'Ninguno'}")

    # Intenta seleccionar y hacer clic
    if lista_certificados:
        _seleccionar_certificado(lista_certificados, nombre_certificado)
        _click_boton_aceptar(ventana_chrome)
        return True
    else:
        return False