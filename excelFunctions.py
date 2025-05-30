"""
Módulo: excelFunctions.py

Este módulo contiene funciones para procesar información proveniente de archivos Excel y 
automatizar la adición de empresas y centros en la aplicación Nubelus utilizando Selenium WebDriver.

Funciones principales:
    - _esperar_descarga(carpeta, extension=".xlsx", timeout=30):
          Espera a que se complete la descarga de un archivo con la extensión indicada en la carpeta especificada.
    - _nif_no_encontrados_en_nubelus(cif_nubelus, datos_recogidas):
          Retorna un DataFrame con las filas cuyos NIF (cif_recogida) no se encuentran en la lista de Nubelus.
    - sacarEmpresasNoAñadidas(driver):
          Procesa los archivos Excel para obtener los datos de empresas que no se han añadido en Nubelus.
    - añadirEmpresas(driver, empresas_añadir):
          Itera sobre el DataFrame 'empresas_añadir' y realiza las acciones necesarias para añadir cada empresa mediante Selenium.
    - sacar_centros_no_encontrados_en_nubelus(centros_nubelus, datos_recogidas):
          Filtra los centros que no han sido encontrados en Nubelus a partir de la columna "nombre_recogida".
    - sacar_centros_no_añadidos(driver):
          Procesa los archivos Excel para obtener los centros medioambientales que no han sido añadidos.
    - añadirCentros(driver, centro_añadir):
          Itera sobre el DataFrame 'centro_añadir' y realiza las acciones necesarias para añadir cada centro en la aplicación.

Ejemplo de uso:
    empresas = sacarEmpresasNoAñadidas(driver)
    añadirEmpresas(driver, empresas)
    
    centros = sacar_centros_no_añadidos(driver)
    añadirCentros(driver, centros)
"""

import glob
import os
import time
import pandas as pd
import json
import logging
import re
import webFunctions
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

# Directorio donde se espera la descarga de archivos Excel
DOWNLOAD_DIR = os.path.join(os.path.expanduser("~"), "Downloads")
# Ruta del archivo Excel recogidas
#EXCEL_RECOGIDAS = r"C:\Users\Metalls1\Downloads\excel_recogidas.xls"

EXCEL_RECOGIDAS = "data/excel_recogidas.xls"
data_recogidas = pd.read_excel(EXCEL_RECOGIDAS)

dic_formas_juridicas = {
    "A": "Sociedades anónimas",
    "B": "Sociedades de responsabilidad limitada",
    "C": "Sociedades colectivas",
    "D": "Sociedades comanditarias",
    "E": "Comunidades de bienes y herencias yacentes",
    "F": "Sociedades cooperativas",
    "G": "Asociaciones",
    "H": "Comunidades de propietarios en régimen de propiedad horizontal",
    "J": "Sociedades civiles, con o sin personalidad jurídica",
    "N": "Entidades extranjeras",
    "P": "Corporaciones Locales",
    "Q": "Organismos públicos",
    "R": "Congregaciones e instituciones religiosas",
    "S": "Órganos de la Administración del Estado y de las Comunidades Autónomas",
    "U": "Uniones Temporales de Empresas",
    #"V": "Sociedad Agraria de Transformación",
    "W": "Establecimientos permanentes de entidades no residentes en España"
}

dic_codigos_residuos_valencia = {
    "A01": "Agente de residuos peligrosos",
    "A02": "Agente de residuos no peligrosos",
    "E01": "Gestor de tratamiento de residuos peligrosos",
    "E02": "Gestor de tratamiento de residuos no peligrosos",
    "G01": "Centro Gestor de residuos peligrosos",
    "G02": "Centro Gestor intermedio de residuos peligrosos (almacenamiento)",
    #"G03": "Transportista de residuos peligrosos asumiendo titularidad (Recogedor)",
    "G04": "Centro Gestor de residuos no peligrosos",
    "G05": "Centro Gestor intermedio de residuos no peligrosos (almacenamiento)",
    "G06": "Plataforma logística de RAEE",
    "N01": "Negociante de residuos peligrosos",
    "N02": "Negociante de residuos no peligrosos",
    "P01": "Productor de residuos peligrosos",
    "P02": "Pequeño productor de residuos peligrosos",
    "P03": "Productor de residuos no peligrosos",
    "P04": "Actividad productora de Residuos No Peligrosos en cantidad inferior a 1000 tn anuales y por tanto no sometida al régimen de comu",
    "P05": "Poseedor de residuos y, por tanto, no sometido a régimen de autorización o comunicación (accidentes, obras puntuales, comunidade",
    "SCR": "Sistema colectivo de Responsabilidad ampliada",
    "SIR": "Sistema individual de Responsabilidad ampliada",
    "T01": "Transportista de residuos peligrosos",
    "T02": "Transportista de residuos no peligrosos"
}

def _esperar_descarga(carpeta: str, extension: str = ".xlsx", timeout: int = 30) -> str:
    """
    Espera a que se descargue un archivo con la extensión especificada en la carpeta indicada.
    
    Args:
        carpeta (str): Ruta del directorio donde se espera la descarga.
        extension (str, opcional): Extensión del archivo buscado. Valor por defecto ".xlsx".
        timeout (int, opcional): Tiempo máximo de espera en segundos.
        
    Returns:
        str: Ruta del archivo descargado.
        
    Raises:
        TimeoutError: Si no se encuentra ningún archivo descargado en el tiempo indicado.
    """
    tiempo_inicio = time.time()
    while time.time() - tiempo_inicio < timeout:
        archivos = glob.glob(os.path.join(carpeta, f"*{extension}"))
        if archivos:
            # Se aseguran de que el archivo no esté en proceso de descarga (sin extensión .crdownload)
            finalizados = [f for f in archivos if not f.endswith('.crdownload')]
            if finalizados:
                return finalizados[0]
        time.sleep(1)
    raise TimeoutError("Descarga no completada en el tiempo esperado.")


def _nif_no_encontrados_en_nubelus(cif_nubelus, datos_recogidas: pd.DataFrame) -> pd.DataFrame:
    """
    Filtra del DataFrame 'datos_recogidas' aquellas filas cuyo 'cif_recogida' no se encuentre
    en los valores de 'cif_nubelus'.

    Args:
        cif_nubelus: Serie o lista con los NIF existentes en Nubelus.
        datos_recogidas (pandas.DataFrame): DataFrame con los datos recogidos del Excel.

    Returns:
        pandas.DataFrame: DataFrame con las filas cuyos NIF no han sido encontrados en Nubelus.
    """
    filas_no_encontradas = []
    for idx, fila in datos_recogidas.iterrows():
        cif_valor = fila['cif_recogida']
        if cif_valor not in cif_nubelus.values:
            filas_no_encontradas.append(fila)
    return pd.DataFrame(filas_no_encontradas)


def sacarEmpresasNoAñadidas(driver: webdriver.Chrome) -> pd.DataFrame:
    """
    Procesa los archivos Excel para identificar las empresas que aún no han sido añadidas en Nubelus.
    
    El proceso consiste en:
      1. Esperar a que se descargue el archivo Excel esperado.
      2. Leer el archivo Excel descargado y el Excel de recogida.
      3. Comparar el NIF de las entidades medioambientales con el listado recogido.
      
    Args:
        driver (webdriver.Chrome): Instancia del navegador.
        
    Returns:
        pandas.DataFrame: DataFrame con los datos de las empresas no añadidas.
        
    Si la descarga falla, se cierra el navegador y se finaliza la ejecución.
    """
    try:
        archivo_xlsx = _esperar_descarga(DOWNLOAD_DIR)
        logging.info(f"Archivo descargado: {archivo_xlsx}")
    except TimeoutError as e:
        logging.error(e)
        driver.quit()
        exit()

    # Leer los Excel con pandas
    entidades_medioambientales = pd.read_excel(archivo_xlsx)
    excel_recogidas = pd.read_excel(EXCEL_RECOGIDAS)

    # Obtener los NIF de Nubelus
    cif_nubelus = entidades_medioambientales["NIF"]

    # Seleccionar únicamente las columnas de interés del Excel recogidas
    datos = excel_recogidas[[
        'cif_recogida', 'nombre_recogida', 'direccion_recogida', 'cp_recogida',
        'poblacion_recogida', 'provincia_recogida', 'email_recogida', 'telf_recogida'
    ]]

    datos_no_encontrados = _nif_no_encontrados_en_nubelus(cif_nubelus, datos)
    return datos_no_encontrados
def forma_juridica(cif: str) -> str:
    """
    Determina la forma jurídica de una empresa según su CIF.

    Args:
        cif (str): El CIF de la empresa.

    Returns:
        str: Forma Jurídica según la primera letra del CIF, o 'Otros' si no se encuentra.
    """
    if not cif or not isinstance(cif, str):
        return "Otros"
    letra = cif.strip().upper()[0]
    return dic_formas_juridicas.get(letra, "Otros")

def añadirEmpresa(driver: webdriver.Chrome, fila) -> None:
    """
    Añade una empresa individualmente en la aplicación web mediante Selenium.

    Args:
        driver (webdriver.Chrome): Instancia del navegador.
        empresa (Union[pandas.Series, dict]): Datos de la empresa a añadir. Puede ser una Serie de pandas o un diccionario.
    """
    try:
        logging.info(f"Añadiendo empresa: {fila['nombre_recogida']}")
        
        # 1. Completar el campo Nombre (con ID "pDenominacion")
        webFunctions.esperar_elemento(driver, By.ID, "pDenominacion", timeout=10)
        webFunctions.escribir_en_elemento_por_id(driver, "pDenominacion", fila["nombre_recogida"]+ " prueba")
        
        # 2. Completar el campo NIF
        webFunctions.escribir_en_elemento_por_name(driver, "pNif", fila["cif_recogida"])
        
        # 3. Completar el campo de forma fiscal: Física si el último carácter del CIF es letra, Jurídica si el primero es letra
        # cif = str(fila["cif_recogida"]).strip()
        # if cif and cif[-1].isalpha():
        #     forma_fiscal = "Física"
        # elif cif and cif[0].isalpha():
        #     forma_fiscal = "Jurídica"
        # webFunctions.seleccionar_elemento_por_nombre(driver, "pForma_fiscal", forma_fiscal)
        
        # # 4. Completar el campo de Forma Jurídica y Nombre Fiscal si es Jurídica
        # if forma_fiscal == "Jurídica":
        #     webFunctions.clickar_elemento(driver,By.CLASS_NAME ,"pDenominacion_forma_juridica")
        #     forma_juridica = forma_juridica(fila["cif_recogida"])
        #     webFunctions.escribir_en_elemento_por_name(driver, "pDenominacion_forma_juridica" ,forma_juridica)
        #     webFunctions.escribir_en_elemento_por_name(driver, "pNombre_fiscal", fila["nombre_recogida"] + " prueba")

        # # 4. Completar el campo Nombre y Apellidos si es una persona física
        # elif forma_fiscal == "Física":
        #     nombre_split = str(fila["nombre_recogida"]).split()
        #     webFunctions.escribir_en_elemento_por_name(driver, "pNombre", nombre_split[0] if nombre_split else "")
        #     webFunctions.escribir_en_elemento_por_name(driver, "pApellidos", " ".join(nombre_split[1:]) if len(nombre_split) > 1 else "")

        # Para la prueba
        webFunctions.seleccionar_elemento_por_nombre(driver, "pForma_fiscal", "Física")
        nombre_split = str(fila["nombre_recogida"]).split()
        webFunctions.escribir_en_elemento_por_name(driver, "pNombre", nombre_split[0] if nombre_split else "")
        webFunctions.escribir_en_elemento_por_name(driver, "pApellidos", " ".join(nombre_split[1:]) if len(nombre_split) > 1 else "")


        # 5. Completar el campo Domicilio
        webFunctions.escribir_en_elemento_por_name(driver, "pDomicilio", fila["direccion_recogida"])
        
        # 6. Completar el campo Municipio
        webFunctions.completar_campo_y_confirmar_seleccion_por_name(driver, "pDenominacion_ine_municipio", str(fila["poblacion_recogida"]).rstrip(), "BUSCAR_INE_MUNICIPIO.noref.ui-menu-item")

        # 7. Completar el campo Provincia
        webFunctions.escribir_en_elemento_por_name(driver, "pPoblacion", fila["provincia_recogida"])
        
        # 8. Completar el campo CP
        webFunctions.escribir_en_elemento_por_name(driver, "pCodigoPostal", str(fila["cp_recogida"]))
        
        # 9. Completar el campo Teléfono
        webFunctions.escribir_en_elemento_por_name(driver, "pTelefono", str(fila["telf_recogida"]))
        
        # 10. Completar el campo Email
        webFunctions.escribir_en_elemento_por_name(driver, "pEmail", fila["email_recogida"])
        
        # 11. Confirmar la adición (clic en botón de aceptar o cancelar o guardar según corresponda)
        webFunctions.clickar_boton_por_clase(driver, "miBoton.aceptar")
        
        # Espera para que la acción se procese
        time.sleep(1)
    except Exception as error:
        logging.error(f"Error al añadir la empresa {fila.get('nombre_recogida', '')}: {error}")

def añadirEmpresas(driver: webdriver.Chrome, empresas_añadir: pd.DataFrame) -> None:
    """
    Itera sobre el DataFrame 'empresas_añadir' y realiza las acciones necesarias para 
    añadir cada empresa en la aplicación web mediante Selenium.

    Se asume que el formulario para añadir empresas ya está visible en la aplicación.
    
    Args:
        driver (webdriver.Chrome): Instancia del navegador.
        empresas_añadir (pandas.DataFrame): DataFrame con los datos de las empresas a añadir.
    
    Ejemplo:
        añadirEmpresas(driver, empresas_df)
    """
    for idx, empresa in empresas_añadir.iterrows():
        # Clic en el botón "nuevo"
        webFunctions.clickar_boton_por_clase(driver, "miBoton.nuevo")
        añadirEmpresa(driver, empresa)


def is_denominacion_correcto(nombre_recogida: str, denominacion: str) -> bool:
    """
    Compara dos cadenas (nombre_recogida y denominacion) para determinar si coinciden
    ignorando signos especiales, mayúsculas/minúsculas y contenido entre paréntesis.

    Args:
        nombre_recogida (str): Nombre del centro recogido.
        denominacion (str): Denominación del centro en Nubelus.

    Returns:
        bool: True si todas las palabras de nombre_recogida están en denominacion, False en caso contrario.
    """
    # Convierte a string y mayúsculas
    nombre_recogida = str(nombre_recogida).upper()
    denominacion = str(denominacion).upper()

    # Quita signos especiales
    signos_especiales = ['.', ',', '-', '&', 'Y']
    for signo in signos_especiales:
        nombre_recogida = nombre_recogida.replace(signo, '')
        denominacion = denominacion.replace(signo, '')

    # Elimina contenido entre paréntesis en nombre_recogida
    nombre_recogida = re.sub(r'\(.*?\)', '', nombre_recogida).strip()

    # Divide en palabras y comprueba si todas están en denominacion
    palabras = nombre_recogida.split()
    for palabra in palabras:
        if palabra not in denominacion:
            return False
    return True


def sacar_centros_no_encontrados_en_nubelus(centros_nubelus: pd.DataFrame, datos_recogidas: pd.DataFrame) -> pd.DataFrame:
    """
    Filtra los centros de datos_recogidas cuyos nombres no se encuentran (según comparación flexible)
    en la columna 'Denominación' de centros_nubelus.

    Args:
        centros_nubelus (pandas.DataFrame): DataFrame con columnas 'Denominación' y 'EMA'.
        datos_recogidas (pandas.DataFrame): DataFrame con columna 'nombre_recogida' y otros datos.

    Returns:
        pandas.DataFrame: DataFrame con los centros no encontrados, añadiendo la columna 'EMA' si corresponde.
    """
    filas_no_encontradas = []
    denominacion_to_ema = dict(zip(centros_nubelus['Denominación'], centros_nubelus['EMA']))

    for idx, fila in datos_recogidas.iterrows():
        encontrado = False
        for denominacion in centros_nubelus['Denominación']:
            if is_denominacion_correcto(fila['nombre_recogida'], denominacion):
                encontrado = True
                break
        if not encontrado:
            fila_dict = fila.to_dict()
            # Intenta asociar la EMA si el nombre coincide exactamente, si no, deja vacío
            fila_dict['EMA'] = denominacion_to_ema.get(fila['nombre_recogida'], '')
            filas_no_encontradas.append(fila_dict)

    return pd.DataFrame(filas_no_encontradas)


def sacar_centros_no_añadidos(driver: webdriver.Chrome) -> pd.DataFrame:
    """
    Procesa los archivos Excel para obtener los centros medioambientales que aún no han sido añadidos en Nubelus.
    
    El proceso es el siguiente:
      1. Espera la descarga del archivo Excel.
      2. Lee el archivo Excel descargado y el archivo de recogida.
      3. Selecciona los datos relevantes de cada uno.
      4. Llama a la función de filtrado para identificar centros no encontrados.
      
    Args:
        driver (webdriver.Chrome): Instancia del navegador.
        
    Returns:
        pandas.DataFrame: DataFrame con los centros no añadidos.
    """
    try:
        archivo_xlsx = _esperar_descarga(DOWNLOAD_DIR)
        logging.info(f"Archivo descargado: {archivo_xlsx}")
    except TimeoutError as e:
        logging.error(e)
        driver.quit()
        exit()

    centros_medioambientales = pd.read_excel(archivo_xlsx)
    excel_recogidas = pd.read_excel(EXCEL_RECOGIDAS)

    # Seleccionar columnas de interés
    centros = centros_medioambientales[['Denominación', 'EMA']]
    datos = excel_recogidas[['nombre_recogida', 'direccion_recogida', 'cp_recogida',
                              'poblacion_recogida', 'provincia_recogida', 'email_recogida',
                              'telf_recogida']]

    # Llamar a la función para filtrar centros no encontrados
    sacar_centros_no_encontrados_en_nubelus(centros, datos)
    return datos


def añadirCentro(driver: webdriver.Chrome, fila) -> None:
    """
    Añade un centro individualmente en la aplicación web mediante Selenium.

    Args:
        driver (webdriver.Chrome): Instancia del navegador.
        centro (Union[pandas.Series, dict]): Datos del centro a añadir. Puede ser una Serie de pandas o un diccionario.
    """
    try:
        logging.info(f"Añadiendo centro: {fila['nombre_recogida']}")

        # 1. Completar el campo Denominación
        webFunctions.esperar_elemento(driver, By.ID, "pDenominacion", timeout=10)
        webFunctions.escribir_en_elemento_por_id(driver, "pDenominacion", fila["nombre_recogida"])

        # 2. (Opcional) Completar el campo EMA si fuese necesario
        webFunctions.escribir_en_elemento_por_name(driver, "pNif", fila.get("EMA", ""))

        # 3. Completar el campo Domicilio
        webFunctions.escribir_en_elemento_por_name(driver, "pDomicilio", fila["direccion_recogida"])

        # 4. Completar el campo Municipio
        webFunctions.completar_campo_y_confirmar_seleccion_por_name(
            driver, "pDenominacion_ine_municipio", str(fila["poblacion_recogida"]).rstrip(), "ui-a-value"
        )

        # 5. Completar el campo Provincia
        webFunctions.escribir_en_elemento_por_name(driver, "pPoblacion", fila["provincia_recogida"])

        # 6. Completar el campo CP
        webFunctions.escribir_en_elemento_por_name(driver, "pCodigoPostal", str(fila["cp_recogida"]))

        # 7. Completar el campo Teléfono
        webFunctions.escribir_en_elemento_por_name(driver, "pTelefono", str(fila["telf_recogida"]))

        # 8. Completar el campo Email
        webFunctions.escribir_en_elemento_por_name(driver, "pEmail", fila["email_recogida"])

        # 9. Confirmar la adición (clic en botón de aceptar o guardar)
        webFunctions.clickar_boton_por_clase(driver, "miBoton.aceptar")

        # Espera para que la acción se procese
        time.sleep(1)
    except Exception as error:
        logging.error(f"Error al añadir el centro {fila.get('nombre_recogida', '')}: {error}")

def añadirCentros(driver: webdriver.Chrome, centros_añadir: pd.DataFrame) -> None:
    """
    Itera sobre el DataFrame 'centros_añadir' y añade cada centro usando añadirCentro.
    """
    for idx, centro in centros_añadir.iterrows():
        webFunctions.clickar_boton_por_clase(driver, "miBoton.nuevo")
        añadirCentro(driver, centro)


def extraer_datos_centro_castilla_desde_excel(ruta_excel):
    """
    Lee un archivo Excel (.xls) y devuelve un JSON estructurado con la información de la sede y los centros.
    """
    datos_castilla = pd.read_excel(ruta_excel, header=1)
    ruta_xlsx = ruta_excel.replace('.xls', '.xlsx')
    datos_castilla.to_excel(ruta_xlsx, index=False)

    # Filtra filas donde 'Unnamed: 0' es un número natural (entero positivo)
    filas_naturales = datos_castilla[datos_castilla['Unnamed: 0'].apply(
        lambda x: isinstance(x, (int, float)) and x > 0 and float(x).is_integer()
    )]

    # --- Sede (toma la primera fila válida como ejemplo, ajusta según tu lógica real) ---
    if not filas_naturales.empty:
        fila_empresa = filas_naturales.iloc[0]
        empresa = {
            "nombre": fila_empresa.get('NOMBRE', ''),
            "direccion": fila_empresa.get('DOMICILIO', ''),
            "municipio": fila_empresa.get('LOCALIDAD', ''),
            "telefono": int(fila_empresa.get('TELÉFONO', 0)),
            #"fax": int(fila_empresa.get('FAX', 0)),
            "provincia": fila_empresa.get('PROVINCIA', ''),
        }
    else:
        empresa = {}

    # --- Centros ---
    centros = []
    # Saltamos la primera fila natural (que es la sede) y usamos las siguientes como centros
    for _, fila in filas_naturales.iloc[0:].iterrows():
        try:
            nima_val = int(fila.get('NIMA ', 0))
        except (ValueError, TypeError):
            nima_val = 0
        # Extraer códigos de residuos sin los que están entre paréntesis
        codigos_raw = str(fila.get('TIPO EXPEDIENTEs', ''))
        # Separa por espacios y filtra los que NO están entre paréntesis
        codigos_residuos = [
            cod for cod in codigos_raw.split()
            if not (cod.startswith('(') and cod.endswith(')'))
        ]
        centro = {
            "nombre_centro": fila.get('NOMBRE', ''),
            "nima": nima_val,
            "direccion_centro": fila.get('DOMICILIO', ''),
            "municipio_centro": fila.get('LOCALIDAD', ''),
            "telefono_centro": int(fila.get('TELÉFONO', 0)),
            #"fax": int(fila.get('FAX', 0)),
            "provincia_centro": fila.get('PROVINCIA', ''),
            "codigos_residuos": codigos_residuos
        }
        centros.append(centro)

    resultado = {
        "empresa": empresa,
        "centros": centros
    }
    return resultado


def esperar_y_guardar_datos_centro_json_Castilla(extension=".xls", timeout=60):
    import glob, os, time, logging

    carpeta_descargas = os.path.join(os.path.expanduser("~"), "Downloads")
    tiempo_inicio = time.time()
    archivo_final = None

    while time.time() - tiempo_inicio < timeout:
        archivos = glob.glob(os.path.join(carpeta_descargas, f"*{extension}"))
        finalizados = [f for f in archivos if not f.endswith('.crdownload')]
        if finalizados:
            archivo_final = max(finalizados, key=os.path.getmtime)
            size = -1
            while True:
                new_size = os.path.getsize(archivo_final)
                if new_size == size:
                    break
                size = new_size
                time.sleep(1)
            break

    datos_dict = None
    archivo_xlsx = None
    try:
        if not archivo_final:
            logging.error("No se descargó ningún archivo en el tiempo esperado.")
            return None

        logging.info(f"Archivo descargado: {archivo_final}")
        datos_dict = extraer_datos_centro_castilla_desde_excel(archivo_final)
        logging.info("Datos extraídos del Excel.")
        archivo_xlsx = archivo_final.replace('.xls', '.xlsx')
    finally:
        # Borrar el archivo .xls
        if archivo_final and os.path.exists(archivo_final):
            try:
                os.remove(archivo_final)
                logging.info(f"Archivo eliminado: {archivo_final}")
            except Exception as e:
                logging.error(f"No se pudo eliminar el archivo: {archivo_final}. Error: {e}")

        # Borrar el archivo .xlsx generado
        if archivo_xlsx and os.path.exists(archivo_xlsx):
            try:
                os.remove(archivo_xlsx)
                logging.info(f"Archivo eliminado: {archivo_xlsx}")
            except Exception as e:
                logging.error(f"No se pudo eliminar el archivo: {archivo_xlsx}. Error: {e}")

    return datos_dict

def añadir_horario(driver, fila):
    """
    Navega a la sección 'Otros', abre el pop-up de aviso y añade un horario de prueba.
    """
    try:
        webFunctions.seleccionar_elemento_por_id(driver, "fContenido_seleccionado", "Otros")
        time.sleep(1)
        webFunctions.clickar_boton_con_titulo(driver, "Editar")
        oldDriver = driver
        popup = webFunctions.encontrar_pop_up_por_id(driver, "div_cambiar_aviso")
        str_horario = "MAÑANAS: " + str(fila.get("horario_m_1", "")) + " - " + str(fila.get("horario_m_2", "")) + "\n" + \
            "TARDES: " + str(fila.get("horario_t_1", "")) + " - " + str(fila.get("horario_t_2", ""))
        webFunctions.escribir_en_elemento_por_name(popup, "pAviso", str_horario)
        webFunctions.clickar_boton_por_clase(popup, "miBoton.aceptar")
        driver = oldDriver
    except Exception as error:
        logging.error(f"Error al añadir horario para la empresa.")

def rellenar_datos_medioambientales(driver, fila):
    """
    Rellena los datos medioambientales en el formulario correspondiente usando los datos de la fila 'empresa'.
    """
    try:
        webFunctions.seleccionar_elemento_por_id(driver, "fContenido_seleccionado", "Datos medioambientales")
        time.sleep(1)
        webFunctions.clickar_boton_por_clase(driver, "miBoton.editar.solapa_descripcion")

        oldDriver = driver
        popup = webFunctions.encontrar_pop_up_por_id(driver, "div_editar_DATOS_MEDIOAMBIENTALES")

        # Rellenar campos con los datos de la empresa
        nima_str = str(fila.get("nima_codigo", ""))
        webFunctions.escribir_en_elemento_por_name(popup, "pNima", nima_str[:10])
        webFunctions.escribir_en_elemento_por_name(popup, "pResponsable_ma_nombre", str(fila.get("nombre_recogida", "")))
        #webFunctions.escribir_en_elemento_por_name(popup, "pResponsable_ma_apellidos", str(datos.get("responsable_apellidos", "")))
        webFunctions.escribir_en_elemento_por_name(popup, "pResponsable_ma_nif", str(fila.get("cif_recogida", "")))
        webFunctions.escribir_en_elemento_por_name(popup, "pResponsable_ma_cargo", str(fila.get("nombre_recogida", "")))
        #webFunctions.completar_campo_y_confirmar_seleccion_por_name(driver, "pDenominacion_ine_vial", str(datos.get("denominacion_vial", "")), "ui-a-label")
        webFunctions.escribir_en_elemento_por_name(popup, "pCodigo_prtr", str(fila.get("poblacion_recogida", "")))

        webFunctions.clickar_boton_por_clase(popup, "miBoton.aceptar")
        driver = oldDriver
    except Exception as error:
        logging.error(f"Error al rellenar datos medioambientales para la empresa {fila.get('nombre_recogida', '')}: {error}")
    
def obtener_fecha_modificada(fecha):
    """
    Obtiene la fecha y la convierte de formato YYYY-MM-DD a DD-MM-YYYY si es posible.

    Args:
        fecha (str): Fecha en formato string.

    Returns:
        str: Fecha en formato DD-MM-YYYY o la original si no es posible convertir.
    """
    fecha = str(fecha)[:10]  # Truncar a longitud 10
    if len(fecha) == 10 and fecha[4] == '-' and fecha[7] == '-':
        partes = fecha.split('-')
        fecha_modificada = f"{partes[2]}-{partes[1]}-{partes[0]}"
    else:
        fecha_modificada = fecha
    return fecha_modificada

def fecha_caducidad(fecha_inicio):
    """
    Recibe una fecha en formato DD-MM-YYYY, suma 5 años y resta un día.
    Devuelve la fecha resultante en el mismo formato DD-MM-YYYY.
    """
    # Extraer día, mes y año
    try:
        partes = str(fecha_inicio)[:10].split('-')
        dia = int(partes[0])
        mes = int(partes[1])
        anio = int(partes[2])

        # Sumar 5 años
        nuevo_anio = anio + 5

        # Restar un día
        dia -= 1
        if dia == 0:
            mes -= 1
            if mes == 0:
                mes = 12
                nuevo_anio -= 1
            # Días por mes (considerando años bisiestos para febrero)
            if mes == 2:
                if (nuevo_anio % 4 == 0 and (nuevo_anio % 100 != 0 or nuevo_anio % 400 == 0)):
                    dia = 29
                else:
                    dia = 28
            elif mes in [1,3,5,7,8,10,12]:
                dia = 31
            else:
                dia = 30

        return f"{dia:02d}-{mes:02d}-{nuevo_anio:04d}"
    except Exception:
        return fecha_inicio

def añadir_acuerdo_representacion(driver, fila):
    """
    Navega a la sección de acuerdos de representación y añade un acuerdo usando los datos de la fila 'empresa'.
    """
    try:
        time.sleep(1)
        webFunctions.completar_campo_y_confirmar_seleccion_por_name(
            driver, "pDenominacion_ema_representada", str(fila.get("nombre_recogida", "")), "BUSCAR_ENTIDAD_MEDIOAMBIENTAL.noref.ui-menu-item"
        )
        fecha_inicio = obtener_fecha_modificada(str(fila.get("fecha_inicio", "")))
        fecha_fin = obtener_fecha_modificada(str(fila.get("fecha_fin", "")))
        webFunctions.escribir_en_elemento_por_name(driver, "pFecha", fecha_inicio)
        webFunctions.escribir_en_elemento_por_name(driver, "pFecha_caducidad", fecha_fin)
        webFunctions.clickar_boton_por_clase(driver, "miBoton.aceptar")
    except Exception as error:
        logging.error(f"Error al añadir acuerdo de representación para la empresa.")

def codigo_residuos_por_autorizacion(codigo_autorizacion: str) -> str:
    """
    Devuelve la clave del código de residuos si la encuentra como subcadena exacta en el número de autorización.
    Si no encuentra ninguna clave, devuelve una cadena vacía.
    """
    if not codigo_autorizacion or not isinstance(codigo_autorizacion, str):
        return ""
    autorizacion_limpia = ''.join(c for c in codigo_autorizacion if c.isalnum()).upper()
    # Devuelve la clave encontrada o una cadena vacía #
    return next((clave for clave in dic_codigos_residuos_valencia if clave in autorizacion_limpia), "P02")

def denominacion_por_autorizacion(codigo_autorizacion: str) -> str:
    """
    Devuelve la denominación (valor) asociada a la clave del diccionario dic_codigos_residuos_valencia
    si alguna clave está como subcadena en el número de autorización.
    Si no encuentra ninguna clave, devuelve una cadena vacía.
    """
    if not codigo_autorizacion or not isinstance(codigo_autorizacion, str):
        return ""
    autorizacion_limpia = ''.join(c for c in codigo_autorizacion if c.isalnum()).upper()
    for clave, valor in dic_codigos_residuos_valencia.items():
        if clave in autorizacion_limpia:
            return valor
    return codigo_autorizacion

def añadir_autorizaciones(driver, fila):
    """
    Navega a la sección 'Autorizaciones' y añade una autorización usando los datos de la fila 'empresa'.
    """
    try:
        webFunctions.seleccionar_elemento_por_id(driver, "fContenido_seleccionado", "Autorizaciones")
        time.sleep(1)
        webFunctions.clickar_boton_por_texto(driver, "Añadir autorización")

        oldDriver = driver
        popup = webFunctions.encontrar_pop_up_por_id(driver, "div_nuevo_AUTORIZACIONES")

        codigo_autorizacion = str(fila.get("nima_cod_peligrosos", ""))
        webFunctions.escribir_en_elemento_por_name(popup, "pAutorizacion_medioambiental", codigo_autorizacion)
        webFunctions.escribir_en_elemento_por_name(popup, "pDenominacion", denominacion_por_autorizacion(codigo_autorizacion))
        webFunctions.escribir_en_elemento_por_name(popup, "pDenominacion_ema", codigo_residuos_por_autorizacion(codigo_autorizacion))
        time.sleep(1)
        
        webFunctions.clickar_boton_por_clase(driver, "BUSCAR_TIPO_ENTIDAD_MEDIOAMBIENTAL.noref.ui-menu-item")
        webFunctions.clickar_boton_por_clase(popup, "miBoton.aceptar")
        driver = oldDriver
    except Exception as error:
        logging.error(f"Error al añadir autorización para la empresa {fila.get('nombre_recogida', '')}: {error}")

def añadir_usuario(driver, fila):
    """
    Añade un usuario a la empresa usando los datos de la fila 'empresa'.
    
    Args:
        driver (webdriver.Chrome): Instancia del navegador.
        fila (pandas.Series): Fila del DataFrame con los datos de la empresa.
    """
    try:
        
        # Completar campos del formulario
        webFunctions.escribir_en_elemento_por_name(driver, "pUsuario", fila["nombre_recogida"].replace(" ", "") + "prueba")
        webFunctions.escribir_en_elemento_por_name(driver, "pAlias", fila["nombre_recogida"])
        webFunctions.escribir_en_elemento_por_name(driver, "pEmail", fila["email_recogida"])
        webFunctions.escribir_en_elemento_por_name(driver, "pTelefono", fila["telf_recogida"])
        webFunctions.seleccionar_elemento_por_name(driver, "pRol", "EMA")
        webFunctions.completar_campo_y_confirmar_seleccion_por_name(
            driver, "pDenominacion_ema", str(fila.get("nombre_recogida", "")), "BUSCAR_ENTIDAD_MEDIOAMBIENTAL.noref.ui-menu-item"
        )
        webFunctions.completar_campo_y_confirmar_seleccion_por_name(
            driver, "pDenominacion_entidad_ma_centro", str(fila.get("nombre_recogida", "")), "BUSCAR_ENTIDAD_MEDIOAMBIENTAL_CENTRO.noref.ui-menu-item"
        )
        
        # Confirmar la adición
        webFunctions.clickar_boton_por_clase(driver, "miBoton.aceptar")
        
        time.sleep(1)  # Espera para que la acción se procese
    except Exception as error:
        logging.error(f"Error al añadir usuario para la empresa {fila.get('nombre_recogida', '')}: {error}")

def añadir_contrato_tratamiento(driver, fila, residuo):
    """
    Añade un contrato de tratamiento a la empresa usando los datos de la fila 'empresa'.
    
    Args:
        driver (webdriver.Chrome): Instancia del navegador.
        fila (pandas.Series): Fila del DataFrame con los datos de la empresa.
    """
    try:
        fecha_inicio = obtener_fecha_modificada(fila["fecha_inicio"])

        webFunctions.completar_campo_y_enter_por_name(driver, "pFecha", fecha_inicio)
        webFunctions.completar_campo_y_enter_por_name(driver, "pDenominacion_origen", fila["nombre_recogida"])
        webFunctions.completar_campo_y_enter_por_name(driver, "pDenominacion_destino", "METALLS DEL CAMP, S.L.") # METALLS DEL CAMP, S.L. siempre
        time.sleep(0.5)
        webFunctions.completar_campo_y_enter_por_name(driver, "pDenominacion_destino_centro", "METALLS DEL CAMP ( SERRA D") # METALLS DEL CAMP ( SERRA D'ESPADA ) siempre
        time.sleep(0.5)
        # Depende si los residuos son o no peligrosos
        if residuo.get("tipo") == "peligroso":  
            webFunctions.completar_campo_y_enter_por_name(driver, "pDenominacion_autorizacion_destino", "157/G02/CV")
        elif residuo.get("tipo") == "no_peligroso":
            webFunctions.completar_campo_y_enter_por_name(driver, "pDenominacion_autorizacion_destino", "374/G04/CV")
        webFunctions.completar_campo_y_enter_por_name(driver, "pDenominacion_operador_traslados", "ECO TITAN S.L.") # Siempre ECO TITAN
        time.sleep(0.5)
        webFunctions.completar_campo_y_enter_por_name(driver, "pDenominacion_autorizacion_operador_traslados", "87/A01/CV") # 87/A01/CV (hacer)
        webFunctions.completar_campo_y_enter_por_name(driver, "pDenominacion_residuo", residuo.get("nombre", ""))
        webFunctions.escribir_en_elemento_por_name(driver, "pKilos_totales", residuo.get("cantidad", ""))
        webFunctions.clickar_boton_por_clase(driver, "miBoton.aceptar")
    except Exception as error:
        logging.error(f"Error al añadir contrato de tratamiento para la empresa {fila.get('nombre_recogida', '')}: {error}")

def añadir_contratos_tratamientos(driver, fila):
    """
    Añade los contratos de tratamiento para la empresa usando los datos de la fila 'empresa'
    y todos los residuos y cantidades del archivo residuos.txt, junto con su centro y tratamiento asociado.
    Para cada residuo, llama a añadir_contrato_tratamiento y al resto de funciones, pasando el residuo como json.
    """
    residuos_centros = residuos_y_tratamientos_json()
    for item in residuos_centros:
        residuo = item["residuo"]  # residuo es un dict/json
        centro = item["centro"]
        residuo["centro"] = centro  # Añadir el centro al residuo
        webFunctions.clickar_boton_por_clase(driver, "miBoton.nuevo")
        añadir_contrato_tratamiento(driver, fila, residuo)
        time.sleep(1)
        añadir_tratamientos(driver, fila, residuo)
        time.sleep(1)
        añadir_facturacion(driver, fila, residuo)

def crear_notificacion_tratamiento(driver):
  """
  Crea una notificación en la plataforma Nubelus.
  
  Esta función hace clic en el botón 'Crear notificación' y acepta el pop-up correspondiente.
  """
  webFunctions.seleccionar_elemento_por_id(driver, "fContenido_seleccionado", "Notificación")
  time.sleep(1)
  webFunctions.clickar_boton_por_clase(driver, "miBoton.generar_xml")
  time.sleep(1)

def añadir_tratamientos(driver, fila, residuo):
    """
    Añade los tratamientos indicados usando los datos de la fila y el residuo (json).
    Si el residuo es 'BATERIAS DE PLOMO*', añade tratamientos 1 y 2.
    Para el resto, solo añade el tratamiento 1.
    Usa el centro asociado que viene en residuo["centro"].
    """
    webFunctions.seleccionar_elemento_por_id(driver, "fContenido_seleccionado", "Tratamientos")
    time.sleep(1)
    try:
        nombre_residuo = residuo.get("nombre", "").strip().upper()
        centro = residuo.get("centro", {})
        if nombre_residuo == "BATERIAS DE PLOMO*":
            indices = [1, 2]
        else:
            indices = [1]
        for i in indices:
            añadir_tratamiento(driver, fila, residuo, indice=i)
    except Exception as error:
        logging.error(f"Error al añadir tratamientos para el residuo {nombre_residuo} de la empresa {fila.get('nombre_recogida', '')}: {error}")

def añadir_tratamiento(driver, fila, residuo, indice=1):
    """
    Añade un tratamiento individual usando los datos de la fila, el residuo (json) y el índice de tratamiento.
    Usa el centro y tratamiento asociados que vienen en el json de residuo["centro"].

    Args:
        driver (webdriver.Chrome): Instancia del navegador.
        fila (pandas.Series): Fila del DataFrame con los datos de la empresa.
        residuo (dict): Diccionario con los datos del residuo y su centro asociado (debe tener clave 'centro').
        indice (int): Índice del tratamiento (1, 2 o 3).
    """
    try:
        centro = residuo.get("centro", {})
        webFunctions.clickar_boton_por_clase(driver, f"miBoton.editar.editar_{indice}.sinTexto.dcha")
        oldDriver = driver
        popup = webFunctions.encontrar_pop_up_por_id(driver, f"div_editar_tratamiento_posterior_{indice}")
        time.sleep(0.5)
        webFunctions.completar_campo_y_enter_por_name(popup, f"pDenominacion_ema_{indice}", centro.get("centro", ""))
        time.sleep(0.5)
        webFunctions.completar_campo_y_enter_por_name(popup, f"pTratamiento_posterior_{indice}_codigo_ler_2", centro.get("tratamiento", ""))

        time.sleep(1)

        webFunctions.clickar_boton_por_clase(popup, "icon-ok")
        driver = oldDriver
        time.sleep(3)
    except Exception as error:
        logging.error(f"Error al añadir tratamiento {indice} para la empresa {fila.get('nombre_recogida', '')}: {error}")

def editar_notificacion_contratos_tratamiento(driver, fila):

    oldDriver = driver
    popup = webFunctions.encontrar_pop_up_por_clase(driver, "miBoton.editar")

    webFunctions.seleccionar_elemento_por_name(popup, "pNt_notificada_sn", "SI")
    # Completar la funcion

    driver = oldDriver

    webFunctions.clickar_boton_por_clase(driver, "miBoton.notificar.adcr")

def residuos_y_tratamientos_json():
    """
    Lee los archivos residuos.txt y centro_tratamientos.txt y devuelve una lista de diccionarios
    con la información de cada residuo y su centro/tratamiento asociado.
    Si en centro_tratamientos.txt hay un guión '-', se asocia ese centro/tratamiento al residuo correspondiente.
    """

    ruta_residuos = os.path.join("data", "residuos.txt")
    ruta_centros = os.path.join("data", "centro_tratamientos.txt")

    # Leer residuos.txt
    residuos = []
    with open(ruta_residuos, encoding="utf-8") as f:
        lineas = [line.strip() for line in f if line.strip()]
    i = 0

    while i < len(lineas):
        tipo_raw = lineas[i].lower()
        if tipo_raw == "p":
            tipo = "peligroso"
        elif tipo_raw == "n":
            tipo = "no peligroso"
        else:
            tipo = tipo_raw  # Por si acaso
        nombre = lineas[i+1]
        cantidad = lineas[i+2]
        residuos.append({
            "tipo": tipo,
            "nombre": nombre,
            "cantidad": cantidad
        })
        i += 3

    # Leer centro_tratamientos.txt
    centros = []
    with open(ruta_centros, encoding="utf-8") as f:
        lineas = [line.strip() for line in f if line.strip()]
    i = 0
    while i < len(lineas):
        centro = lineas[i]
        tratamiento = lineas[i+1]
        # Si el siguiente es un guión, es un centro vacío para el siguiente residuo
        if i+2 < len(lineas) and lineas[i+2] == "-":
            centros.append({
                "centro": centro,
                "tratamiento": tratamiento
            })
            i += 3  # Saltar el guión
        else:
            centros.append({
                "centro": centro,
                "tratamiento": tratamiento
            })
            i += 2

    # Asociar residuos y centros uno a uno
    resultado = []
    for residuo, centro in zip(residuos, centros):
        resultado.append({
            "residuo": residuo,
            "centro": centro
        })

    return resultado

def añadir_facturacion(driver, fila, residuo):
    webFunctions.seleccionar_elemento_por_id(driver, "fContenido_seleccionado", "Facturación")
    time.sleep(2)

    oldDriver = driver
    webFunctions.clickar_boton_por_on_click(driver, "nuevo_FACTURACION()")
    popup = webFunctions.encontrar_pop_up_por_id(driver, "div_nuevo_FACTURACION")

    webFunctions.completar_campo_y_enter_por_name(popup, "pNombre_cliente", fila.get("nombre_recogida", ""))
    webFunctions.completar_campo_y_enter_por_name(popup, "pDenominacion_producto", residuo.get("nombre", ""))
    residuo_nombre = residuo.get("nombre")

    if residuo_nombre in ["ENVASES PLASTICOS CONTAMINADOS*", "FILTROS DE AIRE"]:
        webFunctions.seleccionar_elemento_por_name(popup, "pCantidad_modo", "Valor fijo")
        webFunctions.completar_campo_y_enter_por_name(popup, "pCantidad_valor", "1")
    time.sleep(2)
    webFunctions.clickar_boton_por_clase(popup, "miBoton.aceptar")
    driver = oldDriver
    time.sleep(2)