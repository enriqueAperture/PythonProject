"""
Módulo: nimaFunctions.py

Este módulo proporciona funciones de alto nivel para automatizar la búsqueda y extracción de información
de centros y gestores en los portales NIMA de Valencia, Madrid, Castilla-La Mancha y Cataluña mediante Selenium.
Las funciones lanzan excepciones con mensajes descriptivos en caso de error, de modo que se pueda devolver un error HTTP adecuado
en el endpoint correspondiente.
"""

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
    Extrae datos de la ficha de un centro en NIMA Valencia y los convierte
    a la estructura estándar.
    """
    # Datos de la empresa
    nombre_empresa = webFunctions.obtener_texto_elemento_por_id(driver, "NOMBREEMPRESA1-0")
    nif = webFunctions.obtener_texto_elemento_por_id(driver, "ENIF1-0")
    direccion = webFunctions.obtener_texto_elemento_por_id(driver, "EDIRECCION1-0")
    codigo_postal = webFunctions.obtener_texto_elemento_por_id(driver, "ECODIPOS1-0")
    provincia = webFunctions.obtener_texto_elemento_por_id(driver, "Text8-0")
    telefono = webFunctions.obtener_texto_elemento_por_id(driver, "ETELEFONO1-0")

    # Datos del centro
    nombre_centro = webFunctions.obtener_texto_elemento_por_id(driver, "NOMBRECENTRO1-0-0")
    nima = webFunctions.obtener_texto_elemento_por_id(driver, "FCENCODCENTRO1-0-0")
    direccion_centro = webFunctions.obtener_texto_elemento_por_id(driver, "FDIRECCION1-0-0")
    provincia_centro = webFunctions.obtener_texto_elemento_por_id(driver, "Text7-0-0")
    codigo_ine = webFunctions.obtener_texto_elemento_por_id(driver, "FCODINE1-0-0")
    telefono_centro = webFunctions.obtener_texto_elemento_por_id(driver, "FTELEFONO1-0-0")

    # Estandarizar datos en la estructura:
    empresa_std = {
        "nif": nif,
        "nombre": nombre_empresa,
        "direccion": direccion,
        "cp": codigo_postal,
        "provincia": provincia,
        "telefono": telefono
    }
    centro_std = {
        "nima": nima,
        "nombre": nombre_centro,
        "direccion": direccion_centro,
        "cp": "",           # No disponemos de CP para el centro en este caso
        "provincia": provincia_centro,
        "codigo_ine": codigo_ine,
        "telefono": telefono_centro
    }
    # Se pueden incluir informaciones adicionales en otro key si se desea, por ejemplo "residuos"
    return {"empresa": empresa_std, "centro": centro_std}

def busqueda_NIMA_Valencia(nif):
    """
    Busca centros asociados a un NIF en NIMA Valencia y devuelve un JSON estándar.
    """
    driver = webConfiguration.configure()
    webFunctions.abrir_web(driver, URL_NIMA_VALENCIA)
    webFunctions.escribir_en_elemento_por_id(driver, "ctl00_ContentPlaceHolder1_txtNIF", nif)
    webFunctions.clickar_boton_por_id(driver, "ctl00_ContentPlaceHolder1_btBuscar")

    empresa = None
    centros = []
    try:
        enlaces = webFunctions.encontrar_elementos(
            driver,
            webFunctions.By.XPATH,
            "//a[starts-with(@id, 'ctl00_ContentPlaceHolder1_gvResultados_ctl') and contains(@id, '_hypGestor')]"
        )
        logging.info(f"Encontrados {len(enlaces)} centros para el NIF {nif}.")
        urls_centros = [enlace.get_attribute("href") for enlace in enlaces]

        for url in urls_centros:
            driver.get(url)
            datos = extraer_datos_valencia(driver)
            if datos:
                # Asumimos que la información de empresa siempre es la misma
                if empresa is None:
                    empresa = datos["empresa"]
                centros.append(datos["centro"])
    except Exception as e:
        logging.error(f"ERROR en Valencia: {e}")
    driver.quit()

    if empresa and centros:
        return {"empresa": empresa, "centros": centros}
    else:
        return {"error": "No se encontraron datos válidos en Valencia."}

def extraer_datos_madrid(driver):
    """
    Extrae y transforma los datos de NIMA Madrid a la estructura estándar.
    """
    # Datos de la empresa
    empresa_std = {
        "nif": webFunctions.leer_texto_por_campo(driver, "NIF:"),
        "nombre": webFunctions.leer_texto_por_campo(driver, "Razón Social:"),
        "direccion": webFunctions.leer_texto_por_campo(driver, "Dirección Sede:"),
        "cp": webFunctions.leer_texto_por_campo(driver, "CP:"),
        "provincia": webFunctions.leer_texto_por_campo(driver, "Provincia:"),
        "telefono": webFunctions.leer_texto_por_campo(driver, "Teléfono:")
    }
    # Datos del centro
    centro_std = {
        "nima": webFunctions.leer_texto_por_campo(driver, "NIMA:"),
        "nombre": webFunctions.leer_texto_por_campo(driver, "Denominación del Centro:"),
        "direccion": webFunctions.leer_texto_por_campo(driver, "Dirección Centro:"),
        "cp": webFunctions.leer_texto_por_campo_indice(driver, "CP:", indice=1),
        "provincia": webFunctions.leer_texto_por_campo_indice(driver, "Provincia:", indice=1),
        "codigo_ine": webFunctions.leer_texto_por_campo_indice(driver, "Código INE Municipio:", indice=1),
        "telefono": webFunctions.leer_texto_por_campo_indice(driver, "Teléfono:", indice=1)
    }
    return {"empresa": empresa_std, "centro": centro_std}

def busqueda_NIMA_Madrid(nif):
    """
    Busca centros asociados a un NIF en NIMA Madrid y devuelve un JSON con la estructura estándar.
    """
    driver = webConfiguration.configure()
    webFunctions.abrir_web(driver, URL_NIMA_MADRID)
    webFunctions.escribir_en_elemento_por_id(driver, "nif", nif)
    webFunctions.clickar_enlace_por_onclick(driver, "buscar('form');")

    empresa = None
    centros = []
    try:
        botones = webFunctions.encontrar_elementos(
            driver,
            webFunctions.By.XPATH,
            "//input[@type='button' and @value='Consultar' and contains(@onclick, 'consultar(')]"
        )
        logging.info(f"Encontrados {len(botones)} centros para el NIF {nif}.")
        for boton in botones:
            try:
                boton.click()
                datos = extraer_datos_madrid(driver)
                if datos:
                    if empresa is None:
                        empresa = datos["empresa"]
                    centros.append(datos["centro"])
            except Exception as e:
                logging.error(f"Error al extraer datos de un centro en Madrid: {e}")
            driver.back()
    except Exception as e:
        logging.error(f"ERROR en Madrid: {e}")
    driver.quit()

    if empresa and centros:
        return {"empresa": empresa, "centros": centros}
    else:
        return {"error": "No se encontraron datos válidos en Madrid."}

def busqueda_NIMA_Castilla(nif):
    """
    Busca centros asociados a un NIF en NIMA Castilla y devuelve un JSON con la estructura estándar.
    Se asume que excelFunctions.esperar_y_guardar_datos_centro_json_Castilla retorna un JSON 
    con claves que se transformarán a la estructura estándar.
    """
    driver = webConfiguration.configure()
    datos_json = None
    try:
        webFunctions.abrir_web(driver, URL_NIMA_CASTILLA)
        webFunctions.clickar_boton_por_id(driver, "enlace_gestores")
        webFunctions.escribir_en_elemento_por_id(driver, "input_NIF_CIF", nif)
        webFunctions.clickar_boton_por_id(driver, "boton_buscar")
        if webFunctions.clickar_imagen_generar_excel(driver):
            datos_json = excelFunctions.esperar_y_guardar_datos_centro_json_Castilla(extension=".xls", timeout=60)
            if not datos_json:
                raise Exception("No se pudieron extraer datos del Excel en Castilla")
            logging.info('Datos extraídos del Excel en Castilla.')
        else:
            logging.info('No se ha encontrado la imagen para generar el Excel.')
    except Exception as e:
        logging.error(f"ERROR en Castilla: {e}")
    driver.quit()

    if datos_json and "empresa" in datos_json and "centro" in datos_json:
        # Transformar datos_json a estándar (ejemplo de transformación)
        empresa_std = {
            "nif": datos_json["empresa"].get("nif", ""),
            "nombre": datos_json["empresa"].get("razon_social", ""),
            "direccion": datos_json["empresa"].get("direccion", ""),
            "cp": datos_json["empresa"].get("cp", ""),
            "provincia": datos_json["empresa"].get("provincia", ""),
            "telefono": datos_json["empresa"].get("telefono", "")
        }
        centro_std = {
            "nima": datos_json["centro"].get("nima", ""),
            "nombre": datos_json["centro"].get("nombre", ""),
            "direccion": datos_json["centro"].get("direccion", ""),
            "cp": datos_json["centro"].get("cp", ""),
            "provincia": datos_json["centro"].get("provincia", ""),
            "codigo_ine": datos_json["centro"].get("codigo_ine", ""),
            "telefono": datos_json["centro"].get("telefono", "")
        }
        return {"empresa": empresa_std, "centros": [centro_std]}
    else:
        return {"error": "No se encontraron datos válidos en Castilla."}

def extraer_datos_cataluña(driver, nif):
    """
    Extrae datos de un centro en NIMA Cataluña y los transforma a la estructura estándar.
    """
    logging.info(f"Buscando NIF: {nif}")
    selector_nif = f"//div[contains(@class, 'col-xs-4') and b[normalize-space(text())='Nif:'] and contains(., '{nif}')]"
    try:
        webFunctions.esperar_elemento(driver, "xpath", selector_nif)
        logging.info("Elemento NIF encontrado")
    except Exception as e:
        logging.error(f"No se encontró el elemento NIF para {nif}: {e}")
        return None

    try:
        texto_div = webFunctions.esperar_y_obtener_texto(driver, "xpath", selector_nif)
        valor_nif = texto_div.split("Nif:")[-1].strip()
    except Exception as e:
        logging.error(f"Error extrayendo NIF: {e}")
        valor_nif = ""

    try:
        selector_nima = "//div[contains(@class, 'col-xs-4') and b[normalize-space(text())='Nima:']]"
        texto_div_nima = webFunctions.esperar_y_obtener_texto(driver, "xpath", selector_nima)
        nima = texto_div_nima.split("Nima:")[-1].strip()
    except Exception as e:
        logging.error(f"Error extrayendo NIMA: {e}")
        nima = ""

    try:
        selector_razon = "//div[contains(@class, 'col-xs-8') and b[normalize-space(text())='Raó social:']]"
        texto_div_razon = webFunctions.esperar_y_obtener_texto(driver, "xpath", selector_razon)
        nombre = texto_div_razon.split("Raó social:")[-1].strip()
    except Exception as e:
        logging.error(f"Error extrayendo razón social: {e}")
        nombre = ""

    # Extraer centros de la tabla y transformarlos a la estructura estándar.
    selector_trs = "//tr[contains(@class, 'llistaopen1') or contains(@class, 'llistaopen2')]"
    centros_std = []
    try:
        filas = webFunctions.encontrar_elementos(driver, webFunctions.By.XPATH, selector_trs)
        for fila in filas:
            celdas = fila.find_elements("tag name", "td")
            if len(celdas) >= 5:
                centro_tmp = {
                    "nima": celdas[0].text.strip(),
                    "nombre": celdas[0].text.strip(),  # Si se dispone de un nombre más específico, usarlo
                    "direccion": celdas[2].text.strip(),
                    "cp": celdas[3].text.strip().replace('\xa0', '').replace('&nbsp;', ''),
                    "provincia": celdas[4].text.strip(),
                    "codigo_ine": "",
                    "telefono": ""
                }
                centros_std.append(centro_tmp)
    except Exception as e:
        logging.error(f"Error extrayendo centros: {e}")

    # Estandarizar la información como datos de empresa y centros.
    empresa_std = {
        "nif": valor_nif,
        "nombre": nombre,
        "direccion": "",
        "cp": "",
        "provincia": "",
        "telefono": ""
    }
    return {"empresa": empresa_std, "centros": centros_std}

def busqueda_NIMA_Cataluña(nif):
    driver = webConfiguration.configure()
    try:
        webFunctions.abrir_web(driver, URL_NIMA_CATALUÑA)
        webFunctions.escribir_en_elemento_por_name(driver, "cercaNif", nif)
        webFunctions.clickar_boton_por_texto(driver, "CERCAR")
        datos = extraer_datos_cataluña(driver, nif)
        if not datos or not datos.get("empresa") or not datos.get("centros"):
            raise Exception("Datos incompletos en Cataluña")
    except Exception as e:
        raise Exception("Error en busqueda_NIMA_Cataluña")
    finally:
        driver.quit()
    return datos