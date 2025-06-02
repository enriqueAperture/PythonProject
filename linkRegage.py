"""
Módulo: linkRegage.py

Este módulo recorre el archivo /output/regage.json, construye el enlace de detalle de expediente de MITECO
para cada registro y lo abre en el navegador utilizando Selenium y las funciones auxiliares de webFunctions.

Flujo general:
  1. Lee todos los objetos del archivo regage.json.
  2. Para cada objeto, construye el enlace personalizado de MITECO.
  3. Abre el enlace en el navegador con Selenium.
  4. Repite el proceso para todos los registros.

Ejemplo de uso:
    Ejecutar este script abrirá secuencialmente todos los enlaces de regage.json en el navegador.
"""

import logging
import os
import json
import time
import certHandler
import downloadFunctions
import webConfiguration
import webFunctions
from config import BASE_DIR, cargar_variables

INFO_CERTS = os.path.join(BASE_DIR, "data", "informacionCerts.txt")
info = cargar_variables(INFO_CERTS)

def main():
    """
    Procesa todos los registros de /output/regage.json, construye el enlace de MITECO y lo abre con Selenium.
    """
    output_path = os.path.join(BASE_DIR, "output", "regage.json")
    if not os.path.exists(output_path):
        print(f"No se encontró el archivo: {output_path}")
        return

    with open(output_path, "r", encoding="utf-8") as f:
        try:
            registros = json.load(f)
        except Exception as e:
            print(f"Error leyendo regage.json: {e}")
            return

    if not isinstance(registros, list):
        registros = [registros]

    for registro in registros:
        regage = registro.get("regage", "")
        nif_productor = registro.get("nif_productor", "")
        nif_representante = registro.get("nif_representante", "")

        linkMiteco = (
            "https://sede.miteco.gob.es/portal/site/seMITECO/area_personal"
            "?btnDetalleProc=btnDetalleProc"
            "&pagina=1"
            f"&idExpediente={regage}"
            "&idProcedimiento=736"
            "&idSubOrganoResp=11"
            f"&idDocIdentificativo={nif_productor}"
            f"&idDocRepresentante={nif_representante}"
            "&idEstadoSeleccionado=-1"
            "&idTipoProcSeleccionado=EN+REPRESENTACION+(CERTIFICADO)"
            f"&regInicial={regage}"
            "&numPagSolSelec=10#no-back-button"
        )

        print(f"Abrir enlace: {linkMiteco}")
        driver = webConfiguration.configure()
        webFunctions.abrir_web(driver, linkMiteco)

        webFunctions.esperar_elemento_por_id(driver, "breadcrumb")

        # Proceso de autenticación y selección de acceso
        webFunctions.clickar_boton_por_value(driver, "acceder")
        webFunctions.clickar_boton_por_texto(driver, "Acceso DNIe / Certificado electrónico")

        # Selección del certificado (utiliza certHandler para buscar y confirmar el certificado deseado)
        certHandler.seleccionar_certificado_chrome(info.get("NOMBRE_CERT"))
        # Esperar unos segundos para que el usuario vea la página antes de cerrar
        time.sleep(10)
    
        download_path = downloadFunctions.setup_descarga(driver, "nombre_productor")
        numDownloads = 3
        # Guardar estado inicial
        old_state = downloadFunctions.snapshot_folder_state(download_path)

        # Abrir web y lanzar descarga
        webFunctions.abrir_web(driver, linkMiteco)  # Limpiar la pestaña actual
        try:
            webFunctions.clickar_boton_por_link(driver, "acuerdo")
        except Exception as e:
            numDownloads = 2
            logging.info(f"Error al hacer clic en el enlace 'acuerdo': {e}")
        webFunctions.clickar_boton_por_link(driver, "datosFormulario")
        webFunctions.clickar_boton_por_link(driver, "formato.pdf")

        # Esperar la descarga
        success = downloadFunctions.wait_for_new_download(download_path, old_state, numDownloads)

        # Cerrar driver y finalizar
        downloadFunctions.finalizar_descarga(driver)
        logging.info(f"\nResultado: {' Descarga detectada' if success else 'No se detectó nada'}")
        time.sleep(10)
        driver.quit()

if __name__ == "__main__":
    main()