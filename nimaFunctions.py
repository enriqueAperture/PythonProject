"""
Módulo: excelFunctions.py

Este módulo contiene funciones para procesar información proveniente de archivos Excel y 
automatizar la busqueda de centros en los buscadores NIMA de Valencia, Madrid y Castilla La Mancha.

Funciones principales:
    - _esperar_descarga(carpeta, extension=".xlsx", timeout=30):
          Espera a que se complete la descarga de un archivo con la extensión indicada en la carpeta especificada con los datos de
          los NIF a buscar.

"""

import glob
import os
import time
import json
import pandas as pd
import logging
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import webFunctions
import webConfiguration
import excelFunctions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# Directorio donde se espera la descarga de archivos Excel
#DOWNLOAD_DIR = os.path.join(os.path.expanduser("~"), "Downloads")
# Ruta del archivo Excel recogidas
#EXCEL_NIF = r"C:\Users\Metalls1\Downloads\excel_recogidas.xls"
#ruta_informe = r"C:\Users\Usuario\Downloads\Resumen.xls"


URL_NIMA_CASTILLA = "https://ireno.castillalamancha.es/forms/geref000.htm"
URL_NIMA_VALENCIA = "https://residuos.gva.es/RES_BUSCAWEB/buscador_residuos_avanzado.aspx"
URL_NIMA_MADRID = "https://gestiona.comunidad.madrid/pcea_nima_web/html/web/InicioAccion.icm"

NIF_PRUEBA = "B43693274" # Es de Toledo
NIF_MADRID = "B88218938" # Es de Madrid

def busqueda_NIMA_Valencia(NIF):
    """
    Función para buscar el los datos del NIF en la web de NIMA Valencia y devolver un JSON con los datos.
    """
    driver = webConfiguration.configure()

    # Abrir Web
    webFunctions.abrir_web(driver, URL_NIMA_VALENCIA)

    # Escribir NIF en la web y clickar buscar
    webFunctions.escribir_en_elemento_por_id(driver, "ctl00_ContentPlaceHolder1_txtNIF", NIF)
    webFunctions.clickar_boton_por_id(driver, "ctl00_ContentPlaceHolder1_btBuscar")
    time.sleep(1)

    # Abrir PDF de datos del NIF
    boton_buscar = webFunctions.abrir_link_por_boton_id(driver, "ctl00_ContentPlaceHolder1_gvResultados_ctl03_hypGestor")
    print(f"Enlace del botón: {boton_buscar}")

    time.sleep(20)
    elementos = driver.find_elements(By.XPATH, "//*")
    print("Elementos visibles en la pantalla (tag_name, id):")
    for elem in elementos:
        elem_id = elem.get_attribute("id")
        if elem_id:
            print(f"{elem.tag_name}: {elem_id}")
    
    # Buscar si existe el id "bobjid_1747723616496"
    try:
        elemento = driver.find_element(By.ID, "bobjid_1747723616496")
        print('El elemento con id "bobjid_1747723616496" SÍ está presente en la página.')
    except Exception:
        print('El elemento con id "bobjid_1747723616496" NO está presente en la página.')

def extraer_texto_campo(driver, campo):
    """
    Busca un <td> que contenga un <b> con el texto 'campo' y devuelve el texto que sigue a ese campo.
    Si no lo encuentra, devuelve None.
    """
    try:
        td = driver.find_element(By.XPATH, f"//td[b[normalize-space(text())='{campo}']]")
        texto_completo = td.text
        valor = texto_completo.split(f"{campo}")[-1].strip()
        return valor
    except Exception:
        return None

def extraer_datos_madrid(driver):
    """
    Extrae los datos principales de la ficha de un centro en la web de NIMA Madrid.
    Devuelve un diccionario con los datos de la sede y del centro.
    """
    # Datos del EMA (sede)
    datos_sede = {
        "NIF": extraer_texto_campo(driver, "NIF:"),
        "nombre_sede": extraer_texto_campo(driver, "Razón Social:"),
        "direccion_sede": extraer_texto_campo(driver, "Dirección Sede:"),
        "municipio_sede": extraer_texto_campo(driver, "Municipio:"),
        "codigo_ine_municipio_sede": extraer_texto_campo(driver, "Código INE Municipio:"),
        "codigo_postal_sede": extraer_texto_campo(driver, "CP:"),
        "provincia_sede": extraer_texto_campo(driver, "Provincia:"),
        "codigo_INE_provincia_sede": extraer_texto_campo(driver, "Código INE Provincia:"),
        "nombre_centro": extraer_texto_campo(driver, "Denominación del Centro:")
    }

    # Datos del centro
    datos_centro = {
        "codigo_NIMA": extraer_texto_campo(driver, "NIMA:"),
        "direccion_centro": extraer_texto_campo(driver, "Dirección Centro:"),
        "municipio_centro": extraer_texto_campo(driver, "Municipio:"),
        "codigo_ine_municipio_centro": extraer_texto_campo(driver, "Código INE Municipio:"),
        "codigo_postal_centro": extraer_texto_campo(driver, "CP:"),
        "provincia_centro": extraer_texto_campo(driver, "Provincia:"),
        "codigo_INE_provincia_centro": extraer_texto_campo(driver, "Código INE Provincia:")
    }

    return {
        "sede": datos_sede,
        "centro": datos_centro
    }

def busqueda_NIMA_Madrid(NIF):
    """
    Función para buscar el NIF en la web de NIMA Madrid y devolver un JSON con los datos.
    """
    driver = webConfiguration.configure()
    webFunctions.abrir_web(driver, URL_NIMA_MADRID)
    webFunctions.escribir_en_elemento_por_id(driver, "nif", NIF)

    # Buscar y hacer click en el enlace <a> con onclick="buscar('form');"
    try:
        enlace_buscar = driver.find_element(By.XPATH, "//a[@onclick=\"buscar('form');\"]")
        enlace_buscar.click()
        print('Click realizado en el enlace de búsqueda.')
    except Exception:
        print('ERROR: El enlace de búsqueda NO está presente en la página.')

    # Buscar y hacer click en el botón <input> con value="Consultar"
    try:
        boton_consultar = driver.find_element(By.XPATH, "//input[@type='button' and @value='Consultar']")
        boton_consultar.click()
        print('Click realizado en el botón Consultar.')
    except Exception:
        print('ERROR: El botón Consultar NO está presente en la página.')

    time.sleep(2)

    # Extraer e imprimir los datos
    datos_json = extraer_datos_madrid(driver)
    print(json.dumps(datos_json, ensure_ascii=False, indent=4))
    return datos_json

def busqueda_NIMA_Castilla(NIF):
    """
    Función para buscar el los datos del NIF en la web de NIMA Castilla y devolver un JSON con los datos.
    """
    driver = webConfiguration.configure()

    # Abrir Web
    webFunctions.abrir_web(driver, URL_NIMA_CASTILLA)
    webFunctions.clickar_boton_por_id(driver, "enlace_gestores")
    webFunctions.escribir_en_elemento_por_id(driver, "input_NIF_CIF", NIF)
    webFunctions.clickar_boton_por_id(driver, "boton_buscar")

    # Esperar a que la imagen para generar el EXCEL esté presente y sea clickeable y hacer click
    try:
        img_excel = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//img[@id='imagen_generarPDF_todos' and contains(@title, 'EXCEL')]"))
        )
        img_excel.click()
        print('Click realizado en la imagen para generar el EXCEL.')
        print('Esperando la descarga del EXCEL...')
    except Exception:
        print('ERROR: No se encontró la imagen para generar el EXCEL.')
        return None

    # Ahora solo espera la descarga y procesa el archivo
    datos_json = excelFunctions.esperar_y_guardar_datos_centro_json_Castilla(extension=".xls", timeout=60)
    print('Datos extraídos del Excel:')
    return datos_json