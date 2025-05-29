import logging
import time
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

def seleccionar_certificado(ventana_cert, nombre_certificado="FRANCISCO JAVIER"):
    """
    Selecciona el certificado que contenga "FRANCISCO JAVIER" utilizando los controles 
    DataItemControl obtenidos mediante obtener_data_item_control(), y hace clic en el botón "Aceptar".
    
    Args:
        ventana_cert: Control de la ventana de certificados.
        nombre_certificado (str, optional): Parte del nombre que debe contener el certificado.
                                             Por defecto "FRANCISCO JAVIER".
    
    Returns:
        bool: True si se pudo seleccionar el certificado y pulsar "Aceptar"; False en caso contrario.
    
    Ejemplo de uso:
        if seleccionar_certificado(ventana_cert):
            logging.info("Certificado seleccionado y confirmado correctamente.")
        else:
            logging.error("No se pudo seleccionar el certificado.")
    """
    import time
    import logging
    # Verificar que se ha obtenido la ventana de certificados
    if not ventana_cert:
        logging.error("No se encontró la ventana de certificado.")
        return False

    # Obtener todos los controles tipo DataItemControl (se asumen que representan los certificados)
    certificados = uiautomationHandler.obtener_data_item_control(ventana_cert)
    if not certificados:
        logging.error("No se encontraron controles de certificado.")
        return False

    # Buscar en la lista el certificado que contenga el nombre deseado
    certificado_encontrado = None
    for cert in certificados:
        time.sleep(0.5)  # Espera breve para estabilidad
        if nombre_certificado in cert.Name:
            certificado_encontrado = cert
            break

    if certificado_encontrado:
        logging.info(f"Certificado encontrado: {certificado_encontrado.Name}. Seleccionándolo...")
        certificado_encontrado.Click()
    else:
        logging.error(f"No se encontró un certificado que contenga '{nombre_certificado}'.")
        return False

    # Una vez seleccionado el certificado, pulsar el botón "Aceptar" en el popup "Diálogo de seguridad de almacén Windows"
    if uiautomationHandler.click_boton(ventana_cert, "Diálogo de seguridad de almacén Windows", "Aceptar", timeout=5):
        logging.info("Se hizo clic en el botón 'Aceptar'.")
        return True
    else:
        logging.error("No se pudo hacer clic en el botón 'Aceptar'.")
        return False

def firmar_en_AutoFirma():
    ventana_chrome = uiautomationHandler.obtener_ventana_chrome()
    uiautomationHandler.esperar_popup_y_ejecutar(
        ventana_chrome,
        "¿Abrir AutoFirma?",
        accion=lambda popup: uiautomationHandler.click_boton(ventana_chrome, "¿Abrir AutoFirma?", "Abrir AutoFirma"),
        timeout=10
    )
    uiautomationHandler.esperar_popup_y_ejecutar(
        ventana_chrome,
        "Seleccione un certificado",
        accion=lambda popup: seleccionar_certificado(ventana_chrome),
        timeout=10
    )
    if seleccionar_certificado(ventana_chrome):
        logging.info("Procediendo con la firma en AutoFirma.")
        # Continuar con el proceso de firma
    else:
        logging.error("No se pudo seleccionar el certificado para AutoFirma.")
