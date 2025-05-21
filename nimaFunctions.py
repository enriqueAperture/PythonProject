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
import pandas
import logging
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import webFunctions
import webConfiguration
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# Directorio donde se espera la descarga de archivos Excel
DOWNLOAD_DIR = os.path.join(os.path.expanduser("~"), "Downloads")
# Ruta del archivo Excel recogidas
EXCEL_NIF = r"C:\Users\Metalls1\Downloads\excel_recogidas.xls"

URL_NIMA_CASTILLA = "https://ireno.castillalamancha.es/forms/geref000.htm"
URL_NIMA_VALENCIA = "https://residuos.gva.es/RES_BUSCAWEB/buscador_residuos_avanzado.aspx"
URL_NIMA_MADRID = "https://gestiona.comunidad.madrid/pcea_nima_web/html/web/InicioAccion.icm"

NIF_PRUEBA = "B43693274"

def clasificacion_municipal_NIMA(NIF):
    return "El NIF pertenece al municipio: "

def busqueda_NIMA_Valencia(NIF):
    """
    Función para buscar el NIF en la web de NIMA Valencia.
    """
    driver = webConfiguration.configure()

    # Abrir Web
    webFunctions.abrir_web(driver, URL_NIMA_VALENCIA)

    # Escribir NIF en la web y clickar buscar
    webFunctions.escribir_en_elemento_por_id(driver, "ctl00_ContentPlaceHolder1_txtNIF", NIF_PRUEBA)
    webFunctions.clickar_boton_por_id(driver, "ctl00_ContentPlaceHolder1_btBuscar")
    time.sleep(1)

    # Abrir PDF de datos del NIF
    boton_buscar = webFunctions.abrir_link_por_boton_id(driver, "ctl00_ContentPlaceHolder1_gvResultados_ctl03_hypGestor")
    print(f"Enlace del botón: {boton_buscar}")


def busqueda_NIMA_Madrid(NIF):
    driver = webConfiguration.configure()

    # Abrir Web
    webFunctions.abrir_web(driver, URL_NIMA_MADRID)

    # Escribir NIF en la web
    webFunctions.escribir_en_elemento_por_id(driver, "nif", NIF_PRUEBA)

    # Introducir la provincia TOLEDO = 45, VALENCIA = 46, MADRID = 28 (PROVINCIAS ORDENADAS POR ORDEN ALFABETICO)
    webFunctions.escribir_en_elemento_por_id(driver, "cdProvincia", "45") # después el tercer argumento será provincia
    time.sleep(3)
    """
    CAMPOS PARA LA LECTURA EN JSON (BUSCAR UN EJEMPLO)
    nombre_EMA ->
    NIF_EMA
    direccion_EMA
    telefono_EMA
    fax_EMA
    nombre_centro
    codigo_NIMA
    direccion_centro
    cp_centro
    municipio_centro
    codigo_INE_municipio
    telefono_centro
    fax_centro
    RESTO
    """

def busqueda_NIMA_Castilla(NIF):
    """
    Función para buscar el NIF en la web de NIMA Castilla.
    """
    driver = webConfiguration.configure()

    # Abrir Web
    webFunctions.abrir_web(driver, URL_NIMA_CASTILLA)

    #Abrir formulario busqueda de gestores
    webFunctions.clickar_boton_por_id(driver, "enlace_gestores")

    # Escribir NIF en la web y clickar buscar
    webFunctions.escribir_en_elemento_por_id(driver, "input_NIF_CIF", NIF_PRUEBA)
    webFunctions.clickar_boton_por_id(driver, "boton_buscar")
    ##webFunctions.clickar_boton_por_texto(driver, "")
    td_element = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//td[contains(text(), 'METALLS DEL CAMP, S.L.U.')]"))
    )
    td_element.click()

    time.sleep(3)
    """
    CAMPOS PARA LA LECTURA EN JSON
    nombre_EMA (NULL) 
    NIF_EMA (NULL)
    direccion_EMA (NULL)
    telefono_EMA (NULL)
    fax_EMA (NULL)
    nombre_centro  
    codigo_NIMA
    domicilio_centro (NULL)
    cp_centro (NULL)
    municipio_centro (NULL)
    codigo_INE_municipio (NULL)
    telefono_centro
    fax_centro
    provincia_centro
    localidad_centro
    RESTO
    """

#busqueda_NIMA_Castilla(NIF_PRUEBA)
#busqueda_NIMA_Madrid(NIF_PRUEBA)
#busqueda_NIMA_Valencia(NIF_PRUEBA)