import logging
import loggerConfig
import time
import uiautomation as auto

import uiautomationHandler


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
    else:
        logging.error("No se encontró el popup de certificado.")

def _click_boton_abrir(ventana_chrome, name: str = '¿Abrir AutoFirma?', timeout=5):
    """Busca y hace clic en el botón 'Aceptar' en el popup de certificado."""
    logging.info("Buscando botón 'Abrir AutoFirma'...")
    popup_cert = ventana_chrome.Control(searchDepth=20, ControlType=auto.ControlType.CustomControl, Name=name)
    if popup_cert.Exists(maxSearchSeconds=timeout):
        boton_abrir = popup_cert.ButtonControl(Name='Abrir AutoFirma')
        if boton_abrir.Exists(maxSearchSeconds=timeout):
            logging.info("¡Botón 'Abrir AutoFirma' encontrado! Haciendo click...")
            boton_abrir.Click()
            return True
        else:
            logging.error("No se encontró el botón 'Abrir AutoFirma' en el popup de certificado.")
            return False
    else:
        logging.error("No se encontró el popup de certificado para buscar el botón 'Abrir AutoFirma'.")
        return False

def firmar_en_AutoFirma():
    ventana_chrome = uiautomationHandler.obtener_ventana_chrome()
    _obtener_pop_up_autofirma(ventana_chrome)
    _click_boton_abrir(ventana_chrome)