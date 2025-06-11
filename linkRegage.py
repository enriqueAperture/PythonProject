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

# Imports básicos de Python
import os
import shutil
import sys
import json
import time
import logging
from typing import Union, Optional, List, Dict
import xml.etree.ElementTree as ET
from datetime import datetime

# Imports de Selenium y WebDriver
from selenium import webdriver
from selenium.common import TimeoutException, NoSuchWindowException, NoSuchFrameException, WebDriverException, NoSuchElementException, ElementNotInteractableException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Imports de uiautomation
import uiautomation as auto
import uiautomationHandler

# Imports propios del proyecto
import certHandler
import downloadFunctions
import webConfiguration
import webFunctions
import loggerConfig
import extraerXMLE3L
from config import BASE_DIR, cargar_variables

# Variables de configuración
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

def procesar_multiple_regages():
    """
    Procesa todos los archivos JSON en la carpeta output.
    Para cada archivo JSON:
      - Se leen todos los registros y se procesan uno a uno.
      - Una vez procesado el archivo, se mueve a la carpeta trash.
    """
    output_dir = os.path.join(BASE_DIR, "output")
    if not os.path.exists(output_dir):
        logging.error(f"No existe la carpeta de output: {output_dir}")
        return

    json_files = [os.path.join(output_dir, f) for f in os.listdir(output_dir) if f.endswith(".json")]
    if not json_files:
        logging.info("No se encontró ningún archivo JSON en output.")
        return

    for json_file in json_files:
        logging.info(f"Procesando archivo: {json_file}")
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                registros = json.load(f)
        except Exception as e:
            logging.error(f"Error al leer {json_file}: {e}")
            continue

        if not isinstance(registros, list):
            registros = [registros]

        for registro in registros:
            procesar_registro(registro)

        # Una vez procesado el archivo, moverlo a la carpeta trash
        trash_dir = os.path.join(BASE_DIR, "trash")
        os.makedirs(trash_dir, exist_ok=True)
        destino = os.path.join(trash_dir, os.path.basename(json_file))
        try:
            shutil.move(json_file, destino)
            logging.info(f"Archivo {os.path.basename(json_file)} movido a {destino}.")
        except Exception as e:
            logging.error(f"Error al mover {json_file} a trash: {e}")

if __name__ == "__main__":
    procesar_multiple_regages()