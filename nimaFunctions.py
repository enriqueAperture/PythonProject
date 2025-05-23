"""
Módulo: nimaFunctions.py

Este módulo proporciona funciones de alto nivel para automatizar la búsqueda y extracción de información
de centros y gestores en los portales NIMA de Valencia, Madrid y Castilla-La Mancha mediante Selenium.
Incluye utilidades para interactuar con los formularios web, descargar y procesar archivos Excel, y
estructurar los datos extraídos en formato JSON.

Funciones principales:
    - busqueda_NIMA_Valencia(NIF): Busca un NIF en el portal de Valencia y devuelve los datos relevantes en JSON.
    - busqueda_NIMA_Madrid(NIF): Busca un NIF en el portal de Madrid y devuelve los datos relevantes en JSON.
    - busqueda_NIMA_Castilla(NIF): Busca un NIF en el portal de Castilla-La Mancha, descarga el Excel y devuelve los datos en JSON.
    - busqueda_NIMA_Cataluña(NIF): Busca un NIF en el portal de Cataluña y devuelve los datos relevantes en JSON.

Dependencias:
    - webFunctions: Funciones auxiliares para interactuar con elementos web mediante Selenium.
    - webConfiguration: Configuración y creación del driver de Selenium.
    - excelFunctions: Funciones para procesar y extraer datos de archivos Excel descargados.
"""

import json
import logging
import webFunctions
import webConfiguration
import excelFunctions

URL_NIMA_CASTILLA = "https://ireno.castillalamancha.es/forms/geref000.htm"
URL_NIMA_VALENCIA = "https://residuos.gva.es/RES_BUSCAWEB/buscador_residuos_avanzado.aspx"
URL_NIMA_MADRID = "https://gestiona.comunidad.madrid/pcea_nima_web/html/web/InicioAccion.icm"
URL_NIMA_CATALUÑA = "https://sdr.arc.cat/sdr/ListNimas.do?menu=G"

def extraer_datos_valencia(driver):
    """
    Extrae los datos principales de la ficha de un centro en la web de NIMA Valencia.
    Devuelve un diccionario con los datos relevantes.
    """
    # Datos de la empresa
    nombre_empresa = webFunctions.obtener_texto_elemento_por_id(driver, "NOMBREEMPRESA1-0")
    nif = webFunctions.obtener_texto_elemento_por_id(driver, "ENIF1-0")
    direccion = webFunctions.obtener_texto_elemento_por_id(driver, "EDIRECCION1-0")
    codigo_postal = webFunctions.obtener_texto_elemento_por_id(driver, "ECODIPOS1-0")
    localidad_provincia_empresa = webFunctions.obtener_texto_elemento_por_id(driver, "Text8-0")
    telefono = webFunctions.obtener_texto_elemento_por_id(driver, "ETELEFONO1-0")

    # Datos del centro
    nombre_centro = webFunctions.obtener_texto_elemento_por_id(driver, "NOMBRECENTRO1-0-0")
    nima = webFunctions.obtener_texto_elemento_por_id(driver, "FCENCODCENTRO1-0-0")
    direccion_centro = webFunctions.obtener_texto_elemento_por_id(driver, "FDIRECCION1-0-0")
    localidad_provincia_centro = webFunctions.obtener_texto_elemento_por_id(driver, "Text7-0-0")
    codigo_ine = webFunctions.obtener_texto_elemento_por_id(driver, "FCODINE1-0-0")
    telefono_centro = webFunctions.obtener_texto_elemento_por_id(driver, "FTELEFONO1-0-0")

    # Códigos de residuos (estos datos son opcionales y a veces dan error)
    try:
        codigo_residuo_1 = webFunctions.obtener_texto_elemento_por_id(driver, "Text10-0-0-0").split()[0]
    except Exception:
        logging.error("No se pudo encontrar el código de residuo 1")
        codigo_residuo_1 = None
    try:
        codigo_residuo_2 = webFunctions.obtener_texto_elemento_por_id(driver, "Text10-0-0-1").split()[0]
    except Exception:
        logging.error("No se pudo encontrar el código de residuo 2")
        codigo_residuo_2 = None

    return {
        "empresa": {
            "nombre_empresa": nombre_empresa,
            "nif": nif,
            "direccion": direccion,
            "codigo_postal": codigo_postal,
            "localidad_provincia_empresa": localidad_provincia_empresa,
            "telefono": telefono
        },
        "centro": {
            "nombre_centro": nombre_centro,
            "nima": nima,
            "direccion_centro": direccion_centro,
            "localidad_provincia_centro": localidad_provincia_centro,
            "codigo_ine": codigo_ine,
            "telefono_centro": telefono_centro
        },
        "codigo_residuo_1": codigo_residuo_1,
        "codigo_residuo_2": codigo_residuo_2
    }

def busqueda_NIMA_Valencia(nif):
    """
    Función para buscar los datos del NIF en la web de NIMA Valencia y devolver un JSON con los datos.
    Solo extrae los datos si encuentra el enlace del gestor.
    """
    driver = webConfiguration.configure()
    # Abrir Web y buscar NIF
    webFunctions.abrir_web(driver, URL_NIMA_VALENCIA)
    webFunctions.escribir_en_elemento_por_id(driver, "ctl00_ContentPlaceHolder1_txtNIF", nif)
    webFunctions.clickar_boton_por_id(driver, "ctl00_ContentPlaceHolder1_btBuscar")

    datos_json = None
    try:
        # Abrir la ficha del gestor solo si existe el enlace
        webFunctions.abrir_link_por_boton_id(driver, "ctl00_ContentPlaceHolder1_gvResultados_ctl03_hypGestor")
        datos_json = extraer_datos_valencia(driver)
        logging.info("Datos de la empresa encontrados y extraídos correctamente.")
    except Exception:
        logging.info('ERROR: No se ha encontrado el enlace del gestor en la página.')
    driver.quit()

    if datos_json:
        return datos_json
    else:
        return None

def extraer_datos_madrid(driver):
    """
    Extrae los datos principales de la ficha de un centro en la web de NIMA Madrid.
    Devuelve un diccionario con los datos de la sede y del centro.
    """
    # Datos del EMA (sede)
    datos_sede = {
        "nif": webFunctions.leer_texto_por_campo(driver, "NIF:"),
        "nombre_sede": webFunctions.leer_texto_por_campo(driver, "Razón Social:"),
        "direccion_sede": webFunctions.leer_texto_por_campo(driver, "Dirección Sede:"),
        "municipio_sede": webFunctions.leer_texto_por_campo(driver, "Municipio:"),
        "codigo_ine_municipio_sede": webFunctions.leer_texto_por_campo(driver, "Código INE Municipio:"),
        "codigo_postal_sede": webFunctions.leer_texto_por_campo(driver, "CP:"),
        "provincia_sede": webFunctions.leer_texto_por_campo(driver, "Provincia:"),
        "codigo_INE_provincia_sede": webFunctions.leer_texto_por_campo(driver, "Código INE Provincia:"),
        "nombre_centro": webFunctions.leer_texto_por_campo(driver, "Denominación del Centro:")
    }

    # Datos del centro
    datos_centro = {
        "nima": webFunctions.leer_texto_por_campo(driver, "NIMA:"),
        "direccion_centro": webFunctions.leer_texto_por_campo(driver, "Dirección Centro:"),
        "municipio_centro": webFunctions.leer_texto_por_campo(driver, "Municipio:"),
        "codigo_ine_municipio_centro": webFunctions.leer_texto_por_campo(driver, "Código INE Municipio:"),
        "codigo_postal_centro": webFunctions.leer_texto_por_campo(driver, "CP:"),
        "provincia_centro": webFunctions.leer_texto_por_campo(driver, "Provincia:"),
        "codigo_INE_provincia_centro": webFunctions.leer_texto_por_campo(driver, "Código INE Provincia:")
    }

    return {
        "sede": datos_sede,
        "centro": datos_centro
    }

def busqueda_NIMA_Madrid(nif):
    """
    Función para buscar el NIF en la web de NIMA Madrid y devolver un JSON con los datos.
    Solo extrae los datos si encuentra el botón Consultar.
    """
    driver = webConfiguration.configure()
    webFunctions.abrir_web(driver, URL_NIMA_MADRID)
    webFunctions.escribir_en_elemento_por_id(driver, "nif", nif)

    # Buscar y hacer click en el enlace <a> con onclick="buscar('form');"
    webFunctions.clickar_enlace_por_onclick(driver, "buscar('form');")

    # Buscar y hacer click en el botón <input> con value="Consultar"
    datos_json = None
    try:
        webFunctions.clickar_boton_por_value(driver, "Consultar")
        logging.info('Click realizado en el botón Consultar.')
        # Extraer e imprimir los datos usando la función de excelFunctions
        datos_json = extraer_datos_madrid(driver)
        logging.info('Datos de la empresa guardados')
    except Exception:
        logging.info('ERROR: El botón Consultar NO está presente en la página.')
    driver.quit()

    if datos_json:
        json.dumps(datos_json, ensure_ascii=False, indent=4)
        return datos_json
    else:
        return None

def busqueda_NIMA_Castilla(nif):
    """
    Función para buscar los datos del NIF en la web de NIMA Castilla y devolver un JSON con los datos.
    Solo extrae los datos si encuentra la imagen para generar el EXCEL.
    """
    driver = webConfiguration.configure()
    # Abrir Web y buscar NIF
    webFunctions.abrir_web(driver, URL_NIMA_CASTILLA)
    webFunctions.clickar_boton_por_id(driver, "enlace_gestores")
    webFunctions.escribir_en_elemento_por_id(driver, "input_NIF_CIF", nif)
    webFunctions.clickar_boton_por_id(driver, "boton_buscar")

    datos_json = None
    try:
        # Esperar a que la imagen para generar el EXCEL esté presente y sea clickeable y hacer click
        if webFunctions.clickar_imagen_generar_excel(driver):
            # Ahora solo espera la descarga y procesa el archivo
            datos_json = excelFunctions.esperar_y_guardar_datos_centro_json_Castilla(extension=".xls", timeout=60)
            logging.info('Datos extraídos del Excel:')
        else:
            logging.info('ERROR: No se ha encontrado la imagen para generar el Excel.')
    except Exception:
        logging.info('ERROR: No se ha podido generar o procesar el Excel.')
    driver.quit()

    if datos_json:
        return datos_json
    else:
        return None

def extraer_datos_cataluña(driver, nif):
    """
    Extrae los datos principales de la ficha de un centro en la web de NIMA Cataluña.
    Devuelve un diccionario con los datos relevantes.
    """
    # Esperar a que aparezca el div con la clase 'col-xs-4' que contenga el NIF buscado
    selector_nif = f"//div[contains(@class, 'col-xs-4') and b[normalize-space(text())='Nif:'] and contains(., '{nif}')]"
    webFunctions.esperar_elemento(driver, "xpath", selector_nif)

    # Extraer NIF
    texto_div_nif = webFunctions.esperar_y_obtener_texto(driver, "xpath", selector_nif)
    valor_nif = texto_div_nif.split("Nif:")[-1].strip() if "Nif:" in texto_div_nif else None

    # Extraer NIMA
    selector_nima = "//div[contains(@class, 'col-xs-4') and b[normalize-space(text())='Nima:']]"
    texto_div_nima = webFunctions.esperar_y_obtener_texto(driver, "xpath", selector_nima)
    nima = texto_div_nima.split("Nima:")[-1].strip() if "Nima:" in texto_div_nima else None

    # Extraer Razón Social
    selector_razon = "//div[contains(@class, 'col-xs-8') and b[normalize-space(text())='Raó social:']]"
    texto_div_razon = webFunctions.esperar_y_obtener_texto(driver, "xpath", selector_razon)
    nombre_centro = None
    if "Raó social:" in texto_div_razon:
        nombre_centro = texto_div_razon.split("Raó social:")[-1].strip()
        nombre_centro = " ".join(nombre_centro.split())

    return {
        "nif": valor_nif,
        "nima": nima,
        "nombre_centro": nombre_centro
    }

def busqueda_NIMA_Cataluña(nif):
    """
    Función para buscar el NIF en la web de NIMA Cataluña y devolver un JSON con los datos.
    Solo extrae los datos si encuentra el div con el NIF buscado.
    """
    driver = webConfiguration.configure()
    webFunctions.abrir_web(driver, URL_NIMA_CATALUÑA)
    webFunctions.escribir_en_elemento_por_name(driver, "cercaNif", nif)
    webFunctions.clickar_boton_por_texto(driver, "CERCAR")

    datos_json = None
    try:
        datos_json = extraer_datos_cataluña(driver, nif)
    except Exception:
        logging.info('ERROR: No se ha encontrado el div con el NIF buscado en la página.')
    driver.quit()
    if any([datos_json.get("nif"), datos_json.get("nima"), datos_json.get("nombre_centro")]) if datos_json else False:
        return datos_json
    else:
        return None