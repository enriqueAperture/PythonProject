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