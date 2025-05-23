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
import pandas
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
EXCEL_RECOGIDAS = r"C:\Users\Metalls1\Downloads\excel_recogidas.xls"


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


def _nif_no_encontrados_en_nubelus(cif_nubelus, datos_recogidas: pandas.DataFrame) -> pandas.DataFrame:
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
    return pandas.DataFrame(filas_no_encontradas)


def sacarEmpresasNoAñadidas(driver: webdriver.Chrome) -> pandas.DataFrame:
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
    entidades_medioambientales = pandas.read_excel(archivo_xlsx)
    excel_recogidas = pandas.read_excel(EXCEL_RECOGIDAS)

    # Obtener los NIF de Nubelus
    cif_nubelus = entidades_medioambientales["NIF"]

    # Seleccionar únicamente las columnas de interés del Excel recogidas
    datos = excel_recogidas[[
        'cif_recogida', 'nombre_recogida', 'direccion_recogida', 'cp_recogida',
        'poblacion_recogida', 'provincia_recogida', 'email_recogida', 'telf_recogida'
    ]]

    datos_no_encontrados = _nif_no_encontrados_en_nubelus(cif_nubelus, datos)
    return datos_no_encontrados


def añadirEmpresas(driver: webdriver.Chrome, empresas_añadir: pandas.DataFrame) -> None:
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
        try:
            logging.info(f"Añadiendo empresa: {empresa['nombre_recogida']}")
            # Clic en el botón "nuevo"
            webFunctions.clickar_boton_por_clase(driver, "miBoton.nuevo")
            
            # 1. Completar el campo Nombre (con ID "pDenominacion")
            webFunctions.esperar_elemento(driver, By.ID, "pDenominacion", timeout=10)
            webFunctions.escribir_en_elemento_por_id(driver, "pDenominacion", empresa["nombre_recogida"])
            
            # 2. Completar el campo CIF
            webFunctions.escribir_en_elemento_por_name(driver, "pNif", empresa["cif_recogida"])
            
            # 3. Seleccionar el campo Fiscal (se asume opción "Física")
            webFunctions.seleccionar_elemento_por_nombre(driver, "pForma_fiscal", "Física")
            
            # 4. Completar el campo Nombre y Apellidos
            webFunctions.escribir_en_elemento_por_name(driver, "pNombre", str(empresa["nombre_recogida"]).split()[0])
            webFunctions.escribir_en_elemento_por_name(driver, "pApellidos", " ".join(str(empresa["nombre_recogida"]).split()[1:]))
            
            # 5. Completar el campo Domicilio
            webFunctions.escribir_en_elemento_por_name(driver, "pDomicilio", empresa["direccion_recogida"])
            
            # 6. Completar el campo Municipio
            webFunctions.escribir_en_elemento_por_name(driver, "pDenominacion_ine_municipio", str(empresa["poblacion_recogida"]).rstrip())
            time.sleep(1)
            # Buscar si hay una tilde en el nombre de la población y cortar el string en ese punto
            webFunctions.clickar_boton_por_clase(driver, "ui-a-value")

            # 7. Completar el campo Provincia
            webFunctions.escribir_en_elemento_por_name(driver, "pPoblacion", empresa["provincia_recogida"])
            
            # 8. Completar el campo CP
            webFunctions.escribir_en_elemento_por_name(driver, "pCodigoPostal", str(empresa["cp_recogida"]))
            
            # 9. Completar el campo Teléfono
            webFunctions.escribir_en_elemento_por_name(driver, "pTelefono", str(empresa["telf_recogida"]))
            
            # 10. Completar el campo Email
            webFunctions.escribir_en_elemento_por_name(driver, "pEmail", empresa["email_recogida"])
            
            # 11. Confirmar la adición (clic en botón de cancelar o guardar según corresponda)
            webFunctions.clickar_boton_por_clase(driver, "miBoton.cancelar")
            
            # Espera para que la acción se procese
            time.sleep(1)
        except Exception as error:
            logging.error(f"Error al añadir la empresa {empresa['nombre_recogida']}: {error}")


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


def sacar_centros_no_encontrados_en_nubelus(centros_nubelus: pandas.DataFrame, datos_recogidas: pandas.DataFrame) -> pandas.DataFrame:
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

    return pandas.DataFrame(filas_no_encontradas)


def sacar_centros_no_añadidos(driver: webdriver.Chrome) -> pandas.DataFrame:
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

    centros_medioambientales = pandas.read_excel(archivo_xlsx)
    excel_recogidas = pandas.read_excel(EXCEL_RECOGIDAS)

    # Seleccionar columnas de interés
    centros = centros_medioambientales[['Denominación', 'EMA']]
    datos = excel_recogidas[['nombre_recogida', 'direccion_recogida', 'cp_recogida',
                              'poblacion_recogida', 'provincia_recogida', 'email_recogida',
                              'telf_recogida']]

    # Llamar a la función para filtrar centros no encontrados
    sacar_centros_no_encontrados_en_nubelus(centros, datos)
    return datos


def añadirCentros(driver: webdriver.Chrome, centro_añadir: pandas.DataFrame) -> None:
    """
    Itera sobre el DataFrame 'centro_añadir' y realiza las acciones necesarias para añadir cada centro 
    en la aplicación web de Nubelus.

    Se asume que el formulario para añadir centros ya se encuentra visible.

    Args:
        driver (webdriver.Chrome): Instancia del navegador.
        centro_añadir (pandas.DataFrame): DataFrame con los datos de los centros a añadir.

    Ejemplo:
        añadirCentros(driver, centros_df)
    """
    for idx, centro in centro_añadir.iterrows():
        try:
            logging.info(f"Añadiendo centro: {centro['nombre_recogida']}")
            # Clic en el botón "nuevo" para centros
            webFunctions.clickar_boton_por_clase(driver, "miBoton.nuevo")
            
            # 1. Completar el campo Denominación
            webFunctions.esperar_elemento(driver, By.ID, "pDenominacion", timeout=10)
            webFunctions.escribir_en_elemento_por_id(driver, "pDenominacion", centro["nombre_recogida"])
            
            # 2. (Opcional) Completar el campo EMA si fuese necesario
            webFunctions.escribir_en_elemento_por_name(driver, "pNif", centro["EMA"])
            
            # 3. Completar el campo Domicilio
            webFunctions.escribir_en_elemento_por_name(driver, "pDomicilio", centro["direccion_recogida"])
            
            # 4. Completar el campo Municipio
            webFunctions.escribir_en_elemento_por_name(driver, "pDenominacion_ine_municipio", str(centro["poblacion_recogida"]).rstrip())
            time.sleep(1)
            webFunctions.escribir_en_elemento_por_name(driver, "pDenominacion_ine_municipio", Keys.ENTER)
            
            # 5. Completar el campo Provincia
            webFunctions.escribir_en_elemento_por_name(driver, "pPoblacion", centro["provincia_recogida"])
            
            # 6. Completar el campo CP
            webFunctions.escribir_en_elemento_por_name(driver, "pCodigoPostal", str(centro["cp_recogida"]))
            
            # 7. Completar el campo Teléfono
            webFunctions.escribir_en_elemento_por_name(driver, "pTelefono", str(centro["telf_recogida"]))
            
            # 8. Completar el campo Email
            webFunctions.escribir_en_elemento_por_name(driver, "pEmail", centro["email_recogida"])
            
            # 9. Confirmar la adición (clic en botón de aceptar o guardar)
            webFunctions.clickar_boton_por_clase(driver, "miBoton.cancelar")
            
            # Espera para que la acción se procese
            time.sleep(1)
        except Exception as error:
            logging.error(f"Error al añadir la empresa {centro_añadir.iloc[0]['nombre_recogida']}: {error}")


def extraer_datos_centro_castilla_desde_excel(ruta_excel):
    """
    Lee un archivo Excel (.xls) con los datos de un centro de Castilla-La Mancha, convierte el archivo a formato .xlsx,
    y extrae los datos relevantes de la segunda fila como diccionario.

    Args:
        ruta_excel (str): Ruta al archivo Excel (.xls) descargado.

    Returns:
        dict: Diccionario con los datos extraídos del centro.
    """
    datos_castilla = pandas.read_excel(ruta_excel, header=1)
    ruta_xlsx = ruta_excel.replace('.xls', '.xlsx')
    datos_castilla.to_excel(ruta_xlsx, index=False)
    fila = datos_castilla.iloc[1]
    datos = {
        "DOMICILIO": fila.get('DOMICILIO', ''),
        "NIMA": int(fila.get('NIMA ', 0)),
        "nombre_EMA": fila.get('NOMBRE', ''),
        "provincia_EMA": fila.get('PROVINCIA', ''),
        "localidad_EMA": fila.get('LOCALIDAD', ''),
        "telefono_EMA": int(fila.get('TELÉFONO', 0)),
        "email_EMA": fila.get('E-MAIL', '')
    }
    return datos


def esperar_y_guardar_datos_centro_json_Castilla(extension=".xls", timeout=60):
    """
    Espera a que se descargue un archivo con la extensión indicada en la carpeta de descargas,
    extrae los datos relevantes del Excel y devuelve el resultado en formato JSON.
    Después borra el archivo descargado y el .xlsx generado.

    Args:
        extension (str): Extensión del archivo a buscar (por defecto ".xls").
        timeout (int): Tiempo máximo de espera en segundos.

    Returns:
        str: Cadena JSON con los datos extraídos del centro, o None si falla la descarga.
    """

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
        time.sleep(1)

    if not archivo_final:
        logging.error("No se descargó ningún archivo en el tiempo esperado.")
        return None

    logging.info(f"Archivo descargado: {archivo_final}")
    datos_dict = extraer_datos_centro_castilla_desde_excel(archivo_final)
    datos_json = json.dumps(datos_dict, ensure_ascii=False, indent=4)
    logging.info("Datos extraídos del Excel y convertidos a JSON.")

    # Borrar el archivo .xls
    try:
        os.remove(archivo_final)
        logging.info(f"Archivo eliminado: {archivo_final}")
    except Exception as e:
        logging.error(f"No se pudo eliminar el archivo: {archivo_final}. Error: {e}")

    # Borrar el archivo .xlsx generado
    archivo_xlsx = archivo_final.replace('.xls', '.xlsx')
    if os.path.exists(archivo_xlsx):
        try:
            os.remove(archivo_xlsx)
            logging.info(f"Archivo eliminado: {archivo_xlsx}")
        except Exception as e:
            logging.error(f"No se pudo eliminar el archivo: {archivo_xlsx}. Error: {e}")

    return datos_json
