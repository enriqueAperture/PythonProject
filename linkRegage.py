"""
Módulo: linkRegage.py

Este módulo recorre el archivo /output/regage.json, construye el enlace de detalle de expediente de MITECO
para cada registro y lo abre en el navegador utilizando Selenium y las funciones auxiliares de webFunctions y downloadFunctions.

Flujo general:
  1. Lee todos los objetos del archivo regage.json.
  2. Para cada objeto, construye el enlace personalizado de MITECO.
  3. Abre el enlace en el navegador con Selenium, realiza la autenticación y descarga los archivos asociados en una carpeta única por iteración.
  4. Repite el proceso para todos los registros.

Ejemplo de uso:
    Ejecutar este script abrirá secuencialmente todos los enlaces de regage.json en el navegador y descargará los archivos correspondientes.
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

def get_linkMiteco(regage_val, nif_productor, nif_representante):
    """
    Construye el enlace de detalle de expediente de MITECO para un registro dado.
    """
    linkMiteco = (
        "https://sede.miteco.gob.es/portal/site/seMITECO/area_personal"
        "?btnDetalleProc=btnDetalleProc"
        "&pagina=1"
        f"&idExpediente={regage_val}"
        "&idProcedimiento=736"
        "&idSubOrganoResp=11"
        f"&idDocIdentificativo={nif_productor}"
        f"&idDocRepresentante={nif_representante}"
        "&idEstadoSeleccionado=-1"
        "&idTipoProcSeleccionado=EN+REPRESENTACION+(CERTIFICADO)"
        f"&regInicial={regage_val}"
        "&numPagSolSelec=10#no-back-button"
    )
    return linkMiteco

def autenticar_y_seleccionar_certificado(driver):
    """
    Realiza el proceso de autenticación y selección de certificado en la web de MITECO.
    """
    webFunctions.esperar_elemento_por_id(driver, "breadcrumb")
    webFunctions.clickar_boton_por_value(driver, "acceder")
    webFunctions.clickar_boton_por_texto(driver, "Acceso DNIe / Certificado electrónico")
    certHandler.seleccionar_certificado_chrome(info.get("NOMBRE_CERT"))
    time.sleep(5)

def descargar_documentos(driver, linkMiteco, download_path, numDownloads=3):
    """
    Lanza la descarga de los documentos asociados a un expediente MITECO.
    """
    webFunctions.abrir_web(driver, linkMiteco)
    old_state = downloadFunctions.snapshot_folder_state(download_path)

    # Lanzar descargas
    try:
        webFunctions.clickar_boton_por_link(driver, "acuerdo")
    except Exception as e:
        numDownloads = 2
        logging.info(f"Error al hacer clic en el enlace 'acuerdo': {e}")
    webFunctions.clickar_boton_por_link(driver, "datosFormulario")
    webFunctions.clickar_boton_por_link(driver, "formato.pdf")

    # Esperar la descarga
    archivos_descargados = downloadFunctions.wait_for_new_download(download_path, old_state, numDownloads)
    logging.info(f"Archivos descargados: {archivos_descargados}")
    return archivos_descargados

def procesar_registro(registro):
    """
    Procesa un único registro de regage.json: abre el enlace, autentica, descarga y guarda los archivos.
    """
    regage = registro.get("regage", "")
    nif_productor = registro.get("nif_productor", "")
    nif_representante = registro.get("nif_representante", "")
    nombre_productor = registro.get("nombre_productor", "desconocido").replace(" ", "_")
    nombre_residuo = registro.get("nombre_residuo", "desconocido").replace(" ", "_").replace("*", "")

    linkMiteco = get_linkMiteco(regage, nif_productor, nif_representante)
    logging.info(f"Abrir enlace: {linkMiteco}")

    driver = webConfiguration.configure()
    webFunctions.abrir_web(driver, linkMiteco)
    autenticar_y_seleccionar_certificado(driver)

    # Configurar carpeta de descargas única para este producto
    download_path = downloadFunctions.setup_descarga(driver, nombre_productor, nombre_residuo)

    archivos_descargados = descargar_documentos(driver, linkMiteco, download_path)
    downloadFunctions.finalizar_descarga(driver)
    logging.info(f"Descarga finalizada para {nombre_residuo} ({nombre_productor}).")
    driver.quit()
    return archivos_descargados

def procesar_regages():
    """
    Procesa todos los registros de /output/regage.json, construye el enlace de MITECO y lo abre con Selenium.
    Descarga los archivos asociados en una carpeta única por iteración.
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
        procesar_registro(registro)

    logging.info("Proceso completado. Todos los enlaces han sido abiertos y procesados.")

if __name__ == "__main__":
    procesar_regages()