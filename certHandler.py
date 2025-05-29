import loggerConfig
import uiautomation as auto
import time
import logging

import uiautomationHandler

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

def seleccionar_certificado_chrome(nombre_certificado='RICARDO ESCUDE'):
    """Función principal para llegar a la ventana de Chrome, obtener los certificados
    y seleccionar el certificado especificado."""
    ventana_chrome = uiautomationHandler.obtener_ventana_chrome()
    if not ventana_chrome:
        return False

    # Usar la versión modificada de _obtener_lista_certificados
    lista_certificados = uiautomationHandler.esperar_popup_y_ejecutar(
        ventana_chrome,
        "Seleccionar un certificado",
        accion=lambda popup: uiautomationHandler.obtener_data_item_control(popup),
        timeout=10
    )
    if lista_certificados is []:
        logging.warning("La lista de certificados está vacía.")
        return False

    logging.info(f"Primer certificado encontrado: {lista_certificados[0].Name if lista_certificados else 'Ninguno'}")

    # Intenta seleccionar y hacer clic
    if lista_certificados:
        _seleccionar_certificado(lista_certificados, nombre_certificado)
        uiautomationHandler.click_boton(ventana_chrome, "Seleccionar un certificado", "Aceptar")
        return True
    else:
        return False