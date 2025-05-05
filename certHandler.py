import loggerConfig
import logging

import uiautomation as auto
import time

def aceptarCertificado(cert):
    # Esperar a que aparezca la ventana
    logging.info("Esperando la ventana 'Seleccionar un certificado'...")
    cert_window = auto.WindowControl(searchDepth=1, Name="Seleccionar un certificado")
    try:
        cert_window.Exists(maxSearchSeconds=10)  # Espera hasta 10 segundos para que la ventana exista
        logging.info("Ventana encontrada y activa.")
    except TimeoutError:
        logging.error("No se encontró la ventana 'Seleccionar un certificado' en el tiempo esperado.")
        return
    cert_window.Exists(maxSearchSeconds=10)

    # Activar ventana
    cert_window.SetActive()
    time.sleep(0.5)

    # Buscar el control de lista o tabla
    logging.info("Buscando certificados...")
    cert_table = cert_window.ListControl()
    if not cert_table:
        cert_table = cert_window.DataGridControl()

    if cert_table:
        rows = cert_table.GetChildren()
        found = False

        for row in rows:
            row_text = row.Name
            logging.info(f"→ Opción encontrada: {row_text}")
            if cert in row_text:
                logging.info(f"✔ Seleccionando certificado: {cert}")
                row.Click()
                found = True
                break

        if not found:
            logging.error(f"No se encontró el certificado con nombre: {cert}")
            exit(1)
    else:
        logging.error("✖ No se encontró la lista de certificados.")
        exit(1)

    # Hacer clic en Aceptar
    accept_button = cert_window.ButtonControl(Name="Aceptar")
    if accept_button.Exists(3):
        accept_button.Click()
        logging.info("Se hizo clic en Aceptar.")
    else:
        logging.error("Botón 'Aceptar' no encontrado.")