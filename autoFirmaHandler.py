import logging
import loggerConfig
import uiautomation as auto
import uiautomationHandler

def _obtener_radio_buttons(control):
    """
    Recorre recursivamente un control y devuelve todos los controles de tipo RadioButton.
    """
    radios = []
    for child in control.GetChildren():
        if child.ControlTypeName == 'RadioButton':
            radios.append(child)
        else:
            radios.extend(_obtener_radio_buttons(child))
    return radios

def seleccionar_certificado_francisco():
    """
    Selecciona el certificado que contenga "FRANCISCO JAVIER" y hace clic en el botón "Aceptar".
    
    Usa uiautomationHandler para obtener la ventana de Chrome (o de la aplicación de certificados)
    y para hacer clic en el botón, reutilizando funciones ya creadas en el proyecto.
    
    Returns:
        bool: True si se pudo seleccionar el certificado y pulsar "Aceptar"; False en caso contrario.
    
    Ejemplo de uso:
        if seleccionar_certificado_francisco():
            logging.info("Certificado seleccionado y confirmado correctamente.")
        else:
            logging.error("No se pudo seleccionar el certificado.")
    """
    import time
    import logging
    # Obtener la ventana de la aplicación (se asume que la ventana de certificados es la ventana de Chrome)
    ventana_cert = uiautomationHandler.obtener_ventana_chrome()
    if not ventana_cert:
        logging.error("No se encontró la ventana de certificado.")
        return False

    # Obtener todos los controles tipo RadioButton de la ventana
    radio_buttons = _obtener_radio_buttons(ventana_cert)
    if not radio_buttons:
        logging.error("No se encontraron opciones de certificado.")
        return False

    # Buscar el RadioButton que contenga "FRANCISCO JAVIER" en su propiedad Name
    certificado_encontrado = None
    for radio in radio_buttons:
        time.sleep(0.5)
        if "FRANCISCO JAVIER" in radio.Name:
            certificado_encontrado = radio
            break

    if certificado_encontrado:
        logging.info(f"Certificado encontrado: {certificado_encontrado.Name}. Seleccionándolo...")
        certificado_encontrado.Click()
    else:
        logging.error("No se encontró un certificado que contenga 'FRANCISCO JAVIER'.")
        return False

    # Una vez seleccionado, hacer clic en el botón "Aceptar" del diálogo
    if uiautomationHandler.click_boton(ventana_cert, "Seleccionar un certificado", "Aceptar", timeout=5):
        logging.info("Se hizo clic en el botón 'Aceptar'.")
        return True
    else:
        logging.error("No se pudo hacer clic en el botón 'Aceptar'.")
        return False

def firmar_en_AutoFirma():
    ventana_chrome = uiautomationHandler.obtener_ventana_chrome()
    resultado_autofirma = uiautomationHandler.esperar_popup_y_ejecutar(
        ventana_chrome,
        "¿Abrir AutoFirma?",
        accion=lambda popup: uiautomationHandler.click_boton(ventana_chrome, "¿Abrir AutoFirma?", "Abrir AutoFirma"),
        timeout=10
    )
    if seleccionar_certificado_francisco():
        logging.info("Procediendo con la firma en AutoFirma.")
        # Continuar con el proceso de firma
    else:
        logging.error("No se pudo seleccionar el certificado para AutoFirma.")
