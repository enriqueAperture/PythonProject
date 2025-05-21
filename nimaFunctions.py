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

URL_EINFORMA = "https://www.einforma.com/"

driver = webConfiguration.configure()

def obtener_comunidad_por_nif_empresas(nif) -> str:
    """
    Dado un NIF, devuelve la comunidad autónoma correspondiente según el código de provincia.

    Args:
        nif (str): NIF o CIF de la empresa.

    Returns:
        str: Nombre de la comunidad autónoma, o mensaje de error si no es válida.
    """
    codigos_provincias = {
        # Castilla
        "02": "Castilla",    # Albacete
        "16": "Castilla",    # Cuenca
        "19": "Castilla",    # Guadalajara
        "45": "Castilla",    # Toledo
        # Valencia
        "03": "Valencia",    # Alicante
        "12": "Valencia",    # Castellón
        "43": "Valencia",    # pone que es de Tarragona pero fuck it
        "46": "Valencia",    # Valencia
        "53": "Valencia",
        "54": "Valencia",
        "96": "Valencia",
        "97": "Valencia",
        "98": "Valencia",
        # Madrid
        "28": "Madrid",      # Madrid
        "78": "Madrid",
        "79": "Madrid",
        "80": "Madrid",
        "81": "Madrid",
        "82": "Madrid",
        "83": "Madrid",
        "84": "Madrid",
        "85": "Madrid",
        "86": "Madrid",
        "87": "Madrid",
        "88": "Madrid",
    }
    # Extrae los dígitos del NIF y toma los dos primeros números
    numeros = ''.join(filter(str.isdigit, nif))
    codigo = numeros[:2] if len(numeros) >= 2 else None

    return codigos_provincias.get(codigo, "Provincia no permitida o NIF no válido")

def obtener_comunidad_por_nif_autonomos(nif) -> str:   #Esta funcion da la comunidad autónoma de un NIF de autonomo usando einforma.
    print("Es autonomo")    # Cambiarlo cuando tengamos la funcion de einforma
def obtener_comunidad_por_nif(nif) -> str:
    """
    Devuelve la comunidad autónoma correspondiente según el tipo de NIF:
    - Si el primer carácter es una letra, se asume empresa y llama a obtener_comunidad_por_nif_empresas.
    - Si no, se asume autónomo y llama a obtener_comunidad_por_nif_autonomos.

    Args:
        nif (str): NIF o CIF.

    Returns:
        str: Nombre de la comunidad autónoma, o mensaje de error si no es válida.
    """
    if not nif:
        return "NIF no válido"

    if nif[0].isalpha():
        return obtener_comunidad_por_nif_empresas(nif)
    else:
        return obtener_comunidad_por_nif_autonomos(nif)

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

    # Códigos de residuos
    codigo_residuo_1 = webFunctions.obtener_texto_elemento_por_id(driver, "Text10-0-0-0").split()[0]
    codigo_residuo_2 = webFunctions.obtener_texto_elemento_por_id(driver, "Text10-0-0-1").split()[0]

    return {
        "nombre_empresa": nombre_empresa,
        "nif": nif,
        "direccion": direccion,
        "codigo_postal": codigo_postal,
        "localidad_provincia_empresa": localidad_provincia_empresa,
        "telefono": telefono,
        "nombre_centro": nombre_centro,
        "nima": nima,
        "direccion_centro": direccion_centro,
        "localidad_provincia_centro": localidad_provincia_centro,
        "codigo_ine": codigo_ine,
        "telefono_centro": telefono_centro,
        "codigo_residuo_1": codigo_residuo_1,
        "codigo_residuo_2": codigo_residuo_2
    }

def busqueda_NIMA_Valencia(nif):
    """
    Función para buscar los datos del NIF en la web de NIMA Valencia y devolver un JSON con los datos.
    """
    # Abrir Web y buscar NIF
    webFunctions.abrir_web(driver, URL_NIMA_VALENCIA)
    webFunctions.escribir_en_elemento_por_id(driver, "ctl00_ContentPlaceHolder1_txtNIF", nif)
    webFunctions.clickar_boton_por_id(driver, "ctl00_ContentPlaceHolder1_btBuscar")

    # Abrir la ficha del gestor
    webFunctions.abrir_link_por_boton_id(driver, "ctl00_ContentPlaceHolder1_gvResultados_ctl03_hypGestor")

    # Extraer los datos usando una función auxiliar
    datos_json = extraer_datos_valencia(driver)

    # Guardar en archivo y loggear
    with open("datos_empresa.json", "w", encoding="utf-8") as f:
        json.dump(datos_json, f, ensure_ascii=False, indent=4)
    logging.info("Datos de la empresa guardados en datos_empresa.json")
    return datos_json

def extraer_datos_madrid(driver):
    """
    Extrae los datos principales de la ficha de un centro en la web de NIMA Madrid.
    Devuelve un diccionario con los datos de la sede y del centro.
    """
    # Datos del EMA (sede)
    datos_sede = {
        "NIF": webFunctions.leer_texto_por_campo(driver, "NIF:"),
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
        "codigo_NIMA": webFunctions.leer_texto_por_campo(driver, "NIMA:"),
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
    """
    webFunctions.abrir_web(driver, URL_NIMA_MADRID)
    webFunctions.escribir_en_elemento_por_id(driver, "nif", nif)

    # Buscar y hacer click en el enlace <a> con onclick="buscar('form');"
    webFunctions.clickar_enlace_por_onclick(driver, "buscar('form');")

    # Buscar y hacer click en el botón <input> con value="Consultar"
    try:
        webFunctions.clickar_boton_por_value(driver, "Consultar")
        print('Click realizado en el botón Consultar.')
    except Exception:
        print('ERROR: El botón Consultar NO está presente en la página.')

    # Extraer e imprimir los datos usando la función de excelFunctions
    datos_json = extraer_datos_madrid(driver)
    json.dumps(datos_json, ensure_ascii=False, indent=4)
    logging.info('Datos de la empresa guardados')
    return datos_json

def extraer_datos_castilla(datos_castilla):
    """
    Recibe un DataFrame de pandas con los datos del centro y devuelve un diccionario con los datos relevantes.
    No usa pandas directamente, solo espera el DataFrame como argumento.

    Args:
        datos_castilla: DataFrame de pandas con los datos del Excel.

    Returns:
        dict: Diccionario con los datos extraídos del centro.
    """
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

def busqueda_NIMA_Castilla(NIF):
    """
    Función para buscar el los datos del NIF en la web de NIMA Castilla y devolver un JSON con los datos.
    """

    # Abrir Web
    webFunctions.abrir_web(driver, URL_NIMA_CASTILLA)
    webFunctions.clickar_boton_por_id(driver, "enlace_gestores")
    webFunctions.escribir_en_elemento_por_id(driver, "input_NIF_CIF", NIF)
    webFunctions.clickar_boton_por_id(driver, "boton_buscar")

    # Esperar a que la imagen para generar el EXCEL esté presente y sea clickeable y hacer click
    if not webFunctions.clickar_imagen_generar_excel(driver):
        return None

    # Ahora solo espera la descarga y procesa el archivo
    datos_json = excelFunctions.esperar_y_guardar_datos_centro_json_Castilla(extension=".xls", timeout=60)
    logging.info('Datos extraídos del Excel:')
    return datos_json

def busqueda_NIMA(NIF):
    """
    Función principal para buscar el NIF en la web de NIMA según la comunidad autónoma.
    Detecta la comunidad usando obtener_comunidad_por_nif y llama a la función correspondiente.
    Devuelve los datos en JSON.
    """
    comunidad = obtener_comunidad_por_nif(NIF)
    if comunidad == "Valencia":
        return busqueda_NIMA_Valencia(NIF)
    elif comunidad == "Madrid":
        return busqueda_NIMA_Madrid(NIF)
    elif comunidad == "Castilla":
        return busqueda_NIMA_Castilla(NIF)
    else:
        logging.error(f"Comunidad no válida o NIF no reconocido: {comunidad}")
        return None