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
    Busca todos los centros asociados a un NIF en la web de NIMA Valencia y devuelve un JSON con los datos de la empresa
    y una lista de sus centros asociados.
    """
    driver = webConfiguration.configure()
    webFunctions.abrir_web(driver, URL_NIMA_VALENCIA)
    webFunctions.escribir_en_elemento_por_id(driver, "ctl00_ContentPlaceHolder1_txtNIF", nif)
    webFunctions.clickar_boton_por_id(driver, "ctl00_ContentPlaceHolder1_btBuscar")

    empresa = None
    centros = []
    try:
        # Buscar todos los enlaces de gestor en la tabla de resultados y guardar sus URLs
        enlaces = webFunctions.encontrar_elementos(
            driver,
            webFunctions.By.XPATH,
            "//a[starts-with(@id, 'ctl00_ContentPlaceHolder1_gvResultados_ctl') and contains(@id, '_hypGestor')]"
        )
        logging.info(f"Encontrados {len(enlaces)} centros asociados al NIF {nif}.")
        urls_centros = [enlace.get_attribute("href") for enlace in enlaces]

        for url in urls_centros:
            driver.get(url)
            datos_centro = extraer_datos_valencia(driver)
            if datos_centro:
                # Solo guardar los datos de empresa del primer centro
                if empresa is None and "empresa" in datos_centro:
                    empresa = datos_centro["empresa"]
                # Guardar solo los datos del centro
                if "centro" in datos_centro:
                    centros.append(datos_centro["centro"])
            # No es necesario hacer driver.back() porque vamos directo a la siguiente URL
    except Exception as e:
        logging.error(f"ERROR: No se han podido procesar los centros asociados: {e}")
    driver.quit()

    if empresa and centros:
        return {
            "empresa": empresa,
            "centros": centros
        }
    else:
        return None

def extraer_datos_madrid(driver):
    """
    Extrae los datos principales de la ficha de un centro en la web de NIMA Madrid.
    Devuelve un diccionario con los datos de la sede y del centro.
    """
    # Datos del EMA (sede)
    datos_empresa = {
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
        "empresa": datos_empresa,
        "centro": datos_centro
    }

def busqueda_NIMA_Madrid(nif):
    """
    Busca todos los centros asociados a un NIF en la web de NIMA Madrid y devuelve un JSON con los datos de la sede
    y una lista de sus centros asociados.
    """
    driver = webConfiguration.configure()
    webFunctions.abrir_web(driver, URL_NIMA_MADRID)
    webFunctions.escribir_en_elemento_por_id(driver, "nif", nif)
    webFunctions.clickar_enlace_por_onclick(driver, "buscar('form');")

    sede = None
    centros = []
    try:
        # Guarda todos los onclicks de los botones de consultar
        botones = webFunctions.encontrar_elementos(
            driver,
            webFunctions.By.XPATH,
            "//input[@type='button' and @value='Consultar' and contains(@onclick, 'consultar(')]"
        )
        logging.info(f"Encontrados {len(botones)} centros asociados al NIF {nif}.")
        onclicks = [boton.get_attribute("onclick") for boton in botones]

        for onclick in onclicks:
            # Siempre busca el botón por su onclick actual
            boton = webFunctions.encontrar_elemento(
                driver,
                webFunctions.By.XPATH,
                f"//input[@type='button' and @value='Consultar' and @onclick=\"{onclick}\"]"
            )
            boton.click()
            datos_centro = extraer_datos_madrid(driver)
            if datos_centro:
                if sede is None and "sede" in datos_centro:
                    sede = datos_centro["sede"]
                if "centro" in datos_centro:
                    centros.append(datos_centro["centro"])
            driver.back()
    except Exception as e:
        logging.error(f"ERROR: No se han podido procesar los centros asociados: {e}")
    driver.quit()

    if sede and centros:
        return {
            "sede": sede,
            "centros": centros
        }
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

    # --- Agregar el NIF como primer campo en la sección empresa ---
    if datos_json and isinstance(datos_json, dict) and "empresa" in datos_json:
        empresa = datos_json["empresa"]
        # Crear un nuevo diccionario con el NIF como primer campo
        nueva_empresa = {"nif": nif}
        nueva_empresa.update(empresa)
        datos_json["empresa"] = nueva_empresa

    if datos_json:
        return datos_json
    else:
        return None

def extraer_datos_cataluña(driver, nif):
    """
    Extrae los datos principales de la ficha de un centro en la web de NIMA Cataluña.
    Devuelve un diccionario con los datos relevantes y una lista de centros.
    """
    logging.info(f"Buscando NIF: {nif}")
    selector_nif = f"//div[contains(@class, 'col-xs-4') and b[normalize-space(text())='Nif:'] and contains(., '{nif}')]"
    logging.debug(f"Selector NIF: {selector_nif}")
    try:
        webFunctions.esperar_elemento(driver, "xpath", selector_nif)
        logging.info("Elemento NIF encontrado")
    except Exception as e:
        logging.error(f"No se encontró el elemento NIF: {e}")
        logging.debug(f"HTML actual:\n{driver.page_source}")
        return {}

    # Extraer NIF
    try:
        texto_div_nif = webFunctions.esperar_y_obtener_texto(driver, "xpath", selector_nif)
        logging.debug(f"Texto div NIF: {texto_div_nif}")
        valor_nif = texto_div_nif.split("Nif:")[-1].strip() if "Nif:" in texto_div_nif else None
    except Exception as e:
        logging.error(f"Error extrayendo NIF: {e}")
        valor_nif = None

    # Extraer NIMA
    selector_nima = "//div[contains(@class, 'col-xs-4') and b[normalize-space(text())='Nima:']]"
    logging.debug(f"Selector NIMA: {selector_nima}")
    try:
        texto_div_nima = webFunctions.esperar_y_obtener_texto(driver, "xpath", selector_nima)
        logging.debug(f"Texto div NIMA: {texto_div_nima}")
        nima = texto_div_nima.split("Nima:")[-1].strip() if "Nima:" in texto_div_nima else None
    except Exception as e:
        logging.error(f"Error extrayendo NIMA: {e}")
        nima = None

    # Extraer Razón Social
    selector_razon = "//div[contains(@class, 'col-xs-8') and b[normalize-space(text())='Raó social:']]"
    logging.debug(f"Selector Razón Social: {selector_razon}")
    try:
        texto_div_razon = webFunctions.esperar_y_obtener_texto(driver, "xpath", selector_razon)
        logging.debug(f"Texto div Razón Social: {texto_div_razon}")
        nombre_centro = None
        if "Raó social:" in texto_div_razon:
            nombre_centro = texto_div_razon.split("Raó social:")[-1].strip()
            nombre_centro = " ".join(nombre_centro.split())
    except Exception as e:
        logging.error(f"Error extrayendo Razón Social: {e}")
        nombre_centro = None

    # Extraer todos los centros de la tabla
    selector_trs = "//tr[contains(@class, 'llistaopen1') or contains(@class, 'llistaopen2')]"
    logging.debug(f"Selector filas centros: {selector_trs}")
    centros = []
    try:
        filas = webFunctions.encontrar_elementos(driver, webFunctions.By.XPATH, selector_trs)
        for fila in filas:
            celdas = fila.find_elements("tag name", "td")
            if len(celdas) >= 5:
                centro = {
                    "nima_centro": celdas[0].text.strip(),
                    "direccion_centro": celdas[2].text.strip(),
                    "cp_centro": celdas[3].text.strip().replace('\xa0', '').replace('&nbsp;', ''),
                    "municipio_centro": celdas[4].text.strip()
                }
                centros.append(centro)
    except Exception as e:
        logging.error(f"Error extrayendo filas de centros: {e}")

    return {
        "nif": valor_nif,
        "nima": nima,
        "nombre_centro": nombre_centro,
        "centros": centros
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