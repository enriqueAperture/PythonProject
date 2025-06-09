"""
Módulo: mainCertificados.py

Este módulo orquesta el flujo de automatización para la gestión de certificados en la web de MITECO,
utilizando Selenium para interactuar con la interfaz web y uiautomation junto con funciones auxiliares
de autoFirmaHandler y certHandler para la selección del certificado a utilizar (por DNIe o certificado electrónico).

Flujo general:
  1. Procesa todos los archivos XML de la carpeta /input uno a uno.
  2. Para cada XML, ejecuta el flujo de automatización y mueve el XML procesado a /trash/{nombre_productor}.
  3. Cuando no quedan XML, mueve el PDF a la carpeta del último {nombre_productor} en /trash y termina.

Ejemplo de uso:
    Ejecutar este script inicia el flujo de automatización para el proceso de certificados en MITECO.
    Al finalizar, se cierra el navegador.
"""

# Imports básicos de Python
import os
import json
import time
import shutil
import logging
import sys
from typing import Union, Optional, List, Dict
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

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
import autoFirmaHandler
import certHandler
import extraerXMLE3L
import loggerConfig
import webConfiguration
import webFunctions
from config import BASE_DIR, cargar_variables

# Variables de configuración
WEB_MITECO = (
    "https://sede.miteco.gob.es/portal/site/seMITECO/login?"
    "urlLoginRedirect=L3BvcnRhbC9zaXRlL3NlTUlURUNPL3BvcnRsZXRfYnVzP2lkX3Byb2NlZGltaWVudG89NzM2"
    "JmlkZW50aWZpY2Fkb3JfcGFzbz1QUkVJTklDSU8mc3ViX29yZ2Fubz0xMSZwcmV2aW9fbG9naW49MQ=="
)
INPUT_DIR = os.path.join(BASE_DIR, "input")
TRASH_DIR = os.path.join(BASE_DIR, "trash")
INFO_CERTS = os.path.join(BASE_DIR, "data", "informacionCerts.txt")
info = cargar_variables(INFO_CERTS)
PDF_FILE = os.path.join(INPUT_DIR, info.get("NOMBRE_PDF"))

def actualizar_fechas_xml(xml_path):
    """
    Modifica las fechas del XML en las etiquetas <prepared> y atributos NTDate, NTStartDate, NTEndDate de <wasteNT>.
    Guarda el XML sobrescribiendo el original y devuelve el xml_path.
    """
    tree = ET.parse(xml_path)
    root = tree.getroot()

    # Fechas requeridas
    hoy = datetime.now()
    hoy_str = hoy.strftime("%Y-%m-%d")
    hoy_iso = hoy.strftime("%Y-%m-%dT%H:%M:%S")
    start_date = (hoy + timedelta(days=11)).strftime("%Y-%m-%d")
    end_date = (hoy + timedelta(days=3*365)).strftime("%Y-%m-%d")  # Aproximación de 3 años

    # Modificar <prepared>
    for prepared in root.iter("prepared"):
        prepared.text = hoy_iso

    # Modificar atributos de <wasteNT>
    for waste_nt in root.iter("wasteNT"):
        if "NTDate" in waste_nt.attrib:
            waste_nt.set("NTDate", hoy_str)
        if "NTStartDate" in waste_nt.attrib:
            waste_nt.set("NTStartDate", start_date)
        if "NTEndDate" in waste_nt.attrib:
            waste_nt.set("NTEndDate", end_date)

    tree.write(xml_path, encoding="utf-8", xml_declaration=True)
    return xml_path

def guardar_regage_json(data, output_dir):
    """
    Guarda el contenido en un archivo regage.json en output_dir.
    Si ya existe, crea regage_1.json, regage_2.json, etc. para no sobrescribir.
    """
    base_name = "regage"
    ext = ".json"
    filename = base_name + ext
    counter = 1
    full_path = os.path.join(output_dir, filename)
    while os.path.exists(full_path):
        filename = f"{base_name}_{counter}{ext}"
        full_path = os.path.join(output_dir, filename)
        counter += 1
    with open(full_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return full_path

def mover_a_trash(origen, nombre_productor):
    """
    Mueve un archivo a la carpeta /trash/{nombre_productor}.
    """
    destino_dir = os.path.join(TRASH_DIR, nombre_productor)
    os.makedirs(destino_dir, exist_ok=True)
    destino = os.path.join(destino_dir, os.path.basename(origen))
    shutil.move(origen, destino)
    logging.info(f"Archivo '{os.path.basename(origen)}' movido a '{destino_dir}'.")

def rellenar_formulario(driver):
    """
    Rellena el formulario principal de la web de MITECO con los datos del certificado.
    """
    webFunctions.escribir_en_elemento_por_id(driver, "id_direccion", info.get("DIRECCION"))
    webFunctions.seleccionar_elemento_por_id(driver, "id_pais", info.get("PAIS"))
    webFunctions.seleccionar_elemento_por_id(driver, "id_provincia", info.get("PROVINCIA"))
    webFunctions.seleccionar_elemento_por_id(driver, "id_municipio", info.get("MUNICIPIO"))
    webFunctions.escribir_en_elemento_por_id(driver, "id_codigo_postal", info.get("CODIGO_POSTAL"))
    webFunctions.escribir_en_elemento_por_id(driver, "id_correo_electronico", info.get("CORREO_ELECTRONICO"))

def autenticar_y_seleccionar_certificado(driver):
    """
    Realiza el proceso de autenticación y selección de certificado en la web de MITECO.
    """
    webFunctions.clickar_boton_por_value(driver, "acceder")
    webFunctions.clickar_boton_por_texto(driver, "Acceso DNIe / Certificado electrónico")
    certHandler.seleccionar_certificado_chrome(info.get("NOMBRE_CERT"))

def procesar_xml(xml_path):
    """
    Procesa un archivo XML: automatiza el flujo web, ejecuta la firma y extrae la información relevante.
    Si ocurre cualquier error, se informa y se cierra el driver actual.
    """
    logging.info(f"--- Procesando archivo XML: {os.path.basename(xml_path)} ---")
    driver = webConfiguration.configure()
    try:
        webFunctions.abrir_web(driver, WEB_MITECO)
        webFunctions.esperar_elemento_por_id(driver, "breadcrumb")

        autenticar_y_seleccionar_certificado(driver)
        webFunctions.esperar_elemento_por_id(driver, "wrapper", timeout=15)
        rellenar_formulario(driver)

        webFunctions.clickar_boton_por_id(driver, "btnForm")
        time.sleep(5)

        webFunctions.clickar_boton_por_id(driver, "tipoEnvioNtA")
        actualizar_fechas_xml(xml_path)
        webFunctions.escribir_en_elemento_por_id(driver, "file", xml_path)

        webFunctions.clickar_boton_por_clase(driver, "loginBtn")
        webFunctions.clickar_boton_por_texto(driver, "Continuar")
        webFunctions.escribir_en_elemento_por_id(driver, "idFichero", PDF_FILE)
        webFunctions.clickar_boton_por_id(driver, "btnForm")
        webFunctions.clickar_boton_por_id(driver, "bSiguiente")
        webFunctions.clickar_boton_por_id(driver, "idFirmarRegistrar")
        time.sleep(2)
        webFunctions.clickar_boton_por_id(driver, "idFirmarRegistrar")

        autoFirmaHandler.firmar_en_autofirma()

        regage = webFunctions.obtener_texto_por_parte(driver, "Descargar Justificante:").split()[-1]
        logging.info(f"Código de justificante obtenido: {regage}")

        json_result = extraerXMLE3L.extraer_info_xml(xml_path, regage)
        logging.info(f"Información extraída del XML: {json_result}")

        return json_result

    except Exception as e:
        logging.error(f"Error procesando '{os.path.basename(xml_path)}': {e}", exc_info=True)
    finally:
        try:
            driver.quit()
        except Exception as e_quit:
            logging.error(f"Error cerrando driver: {e_quit}")

def procesar_archivos_xml():
    """
    Procesa todos los archivos XML de la carpeta /input, gestionando los errores y moviendo los archivos procesados.
    """
    xml_files = sorted([os.path.join(INPUT_DIR, f) for f in os.listdir(INPUT_DIR) if f.lower().endswith('.xml')])
    ultimo_nombre_productor = None

    while xml_files:
        procesados_esta_vuelta = []
        for xml_file in xml_files:
            try:
                resultado = procesar_xml(xml_file)
                nombre_productor = resultado.get("nombre_productor", "desconocido").replace(" ", "_")
                mover_a_trash(xml_file, nombre_productor)
                ultimo_nombre_productor = nombre_productor
                procesados_esta_vuelta.append(xml_file)
            except Exception as e:
                logging.error(f"Error procesando '{os.path.basename(xml_file)}': {e}")
                # No mover el archivo, se queda en input para el siguiente intento

        # Actualizar la lista de archivos xml para la siguiente vuelta (solo los que no se han procesado)
        xml_files = sorted([os.path.join(INPUT_DIR, f) for f in os.listdir(INPUT_DIR) if f.lower().endswith('.xml')])

        # Si no se ha procesado ningún archivo en esta vuelta, salir para evitar bucle infinito
        if not procesados_esta_vuelta and xml_files:
            logging.error("No se ha podido procesar ninguno de los archivos XML restantes. Revisa los archivos en /input.")
            break

    # Cuando no quedan XML, mover el PDF a la carpeta del último productor
    if ultimo_nombre_productor and os.path.exists(PDF_FILE):
        logging.info(f"Moviendo PDF '{os.path.basename(PDF_FILE)}' a la carpeta '{ultimo_nombre_productor}' en trash.")
        mover_a_trash(PDF_FILE, ultimo_nombre_productor)
    logging.info("Proceso completado. Todos los archivos procesados y movidos.")

def main():
    """
    Función principal que inicia el procesamiento de los archivos XML.
    """
    procesar_archivos_xml()
    logging.info("Todos los procesos han finalizado correctamente.")

if __name__ == "__main__":
    main()