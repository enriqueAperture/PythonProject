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

    # Códigos de residuos (estos datos son opcionales)
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
    Busca los datos del NIF en la web de NIMA Valencia y devuelve un JSON con los datos.
    Lanza una excepción si ocurre algún error o no se pueden extraer los datos.
    """
    driver = webConfiguration.configure()
    try:
        webFunctions.abrir_web(driver, URL_NIMA_VALENCIA)
        webFunctions.escribir_en_elemento_por_id(driver, "ctl00_ContentPlaceHolder1_txtNIF", nif)
        webFunctions.clickar_boton_por_id(driver, "ctl00_ContentPlaceHolder1_btBuscar")
        webFunctions.abrir_link_por_boton_id(driver, "ctl00_ContentPlaceHolder1_gvResultados_ctl03_hypGestor")
        datos_json = extraer_datos_valencia(driver)
        if not datos_json:
            raise Exception("No se pudieron extraer los datos de NIMA Valencia")
        logging.info("Datos de la empresa encontrados y extraídos correctamente en Valencia.")
    except Exception as e:
        raise Exception(f"Error en busqueda_NIMA_Valencia")
    finally:
        driver.quit()
    return datos_json

# Realiza cambios similares en las demás funciones de búsqueda.
# Por ejemplo, en busqueda_NIMA_Madrid, busqueda_NIMA_Castilla y busqueda_NIMA_Cataluña, asegúrate
# de lanzar una excepción con un mensaje descriptivo en caso de error.

def extraer_datos_madrid(driver):
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
    driver = webConfiguration.configure()
    try:
        webFunctions.abrir_web(driver, URL_NIMA_MADRID)
        webFunctions.escribir_en_elemento_por_id(driver, "nif", nif)
        webFunctions.clickar_enlace_por_onclick(driver, "buscar('form');")
        webFunctions.clickar_boton_por_value(driver, "Consultar")
        logging.info('Click realizado en el botón Consultar en Madrid.')
        datos_json = extraer_datos_madrid(driver)
        if not datos_json:
            raise Exception("No se pudieron extraer los datos de NIMA Madrid")
        logging.info('Datos de la empresa extraídos en Madrid.')
    except Exception as e:
        raise Exception(f"Error en busqueda_NIMA_Madrid")
    finally:
        driver.quit()
    return datos_json

def busqueda_NIMA_Castilla(nif):
    driver = webConfiguration.configure()
    try:
        webFunctions.abrir_web(driver, URL_NIMA_CASTILLA)
        webFunctions.clickar_boton_por_id(driver, "enlace_gestores")
        webFunctions.escribir_en_elemento_por_id(driver, "input_NIF_CIF", nif)
        webFunctions.clickar_boton_por_id(driver, "boton_buscar")
        if webFunctions.clickar_imagen_generar_excel(driver):
            datos_json = excelFunctions.esperar_y_guardar_datos_centro_json_Castilla(extension=".xls", timeout=60)
            if not datos_json:
                raise Exception("No se pudieron extraer los datos desde el Excel en Castilla")
            logging.info('Datos extraídos del Excel en Castilla.')
        else:
            raise Exception("No se ha encontrado la imagen para generar el Excel en Castilla")
    except Exception as e:
        raise Exception(f"Error en busqueda_NIMA_Castilla")
    finally:
        driver.quit()
    return datos_json

def extraer_datos_cataluña(driver, nif):
    selector_nif = f"//div[contains(@class, 'col-xs-4') and b[normalize-space(text())='Nif:'] and contains(., '{nif}')]"
    webFunctions.esperar_elemento(driver, "xpath", selector_nif)
    texto_div_nif = webFunctions.esperar_y_obtener_texto(driver, "xpath", selector_nif)
    valor_nif = texto_div_nif.split("Nif:")[-1].strip() if "Nif:" in texto_div_nif else None

    selector_nima = "//div[contains(@class, 'col-xs-4') and b[normalize-space(text())='Nima:']]"
    texto_div_nima = webFunctions.esperar_y_obtener_texto(driver, "xpath", selector_nima)
    nima = texto_div_nima.split("Nima:")[-1].strip() if "Nima:" in texto_div_nima else None

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
    driver = webConfiguration.configure()
    try:
        webFunctions.abrir_web(driver, URL_NIMA_CATALUÑA)
        webFunctions.escribir_en_elemento_por_name(driver, "cercaNif", nif)
        webFunctions.clickar_boton_por_texto(driver, "CERCAR")
        datos_json = extraer_datos_cataluña(driver, nif)
        if not datos_json or not any([
            datos_json.get("nif"), datos_json.get("nima"), datos_json.get("nombre_centro")
        ]):
            raise Exception("No se han extraído datos válidos para NIMA Cataluña")
    except Exception as e:
        raise Exception(f"Error en busqueda_NIMA_Cataluña")
    finally:
        driver.quit()
    return datos_json