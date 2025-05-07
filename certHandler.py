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

def _obtener_lista_certificados(ventana_chrome, timeout=10):
    """Espera y obtiene el control del popup de selección de certificados (versión modificada)."""
    logging.info("Esperando popup de certificado (versión modificada)...")
    popup_cert = None
    start_time = time.time()
    while not popup_cert and (time.time() - start_time) < timeout:
        popup_cert = ventana_chrome.Control(searchDepth=20, ControlType=auto.ControlType.CustomControl,
                                            Name='Seleccionar un certificado')
        if not popup_cert.Exists():
            popup_cert = None
            time.sleep(0.5)

    if popup_cert:
        logging.info("Popup de certificado detectado (versión modificada).")
        certificados = popup_cert.GetChildren()
        logging.info(f"Certificados encontrados (versión modificada): {certificados}")
        return list(certificados)
    else:
        logging.error("No se encontró el popup de certificado (versión modificada).")
        return []

def _seleccionar_certificado(lista_certificados, nombre_certificado):
    """Selecciona el certificado deseado de la lista."""
    cert_encontrado = None
    found = False

    logging.info(f"Buscando certificado '{nombre_certificado}' en la lista...")
    logging.info(f"Buscando certificado '{lista_certificados[0].Exists()}' en la lista...")
    for certificado in lista_certificados:
        logging.info(f"Este es el nombre de uno de los certificados: '{certificado.Show()}'")
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
        logging.warning("No se encontró el certificado deseado. Seleccionando el primero disponible.")
        if lista_certificados:
            primer_certificado = lista_certificados[0]
            logging.info(f"Seleccionando el primer certificado: {primer_certificado.Name}")
            primer_certificado.Click()
            found = True
        else:
            logging.error("No hay certificados disponibles para seleccionar.")

    return found

def _click_boton_aceptar(ventana_chrome, timeout=5):
    logging.info("Entrando en _click_boton_aceptar...")
    """Busca y hace clic en el botón 'Aceptar' en el popup de certificado."""
    logging.info("Buscando botón 'Aceptar'...")
    popup_cert = ventana_chrome.Control(searchDepth=20, ControlType=auto.ControlType.CustomControl,
                                        Name='Seleccionar un certificado')
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
    y seleccionar el certificado especificado.
    """
    #logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    ventana_chrome = _obtener_ventana_chrome()
    if not ventana_chrome:
        return False

    # Usar la versión modificada de _obtener_lista_certificados
    lista_certificados = _obtener_lista_certificados(ventana_chrome)
    if not lista_certificados:
        logging.warning("La lista de certificados está vacía.")
        return False

    logging.info(
        f"Primer certificado encontrado: {lista_certificados[0].Name if lista_certificados else 'Ninguno'}")

    # Intenta seleccionar y hacer clic
    if lista_certificados:
        _seleccionar_certificado(lista_certificados, nombre_certificado)
        _click_boton_aceptar(ventana_chrome)
        return True
    else:
        return False