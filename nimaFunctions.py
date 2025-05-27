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
            "direccion_empresa": direccion,
            "cp_empresa": codigo_postal,
            "provincia_empresa": localidad_provincia_empresa,
            "telefono_empresa": telefono
        },
        "centro": {
            "nombre_centro": nombre_centro,
            "nima": nima,
            "direccion_centro": direccion_centro,
            "provincia_centro": localidad_provincia_centro,
            "codigo_ine_centro": codigo_ine,
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
    """
    Extrae los datos principales de la ficha de un centro en la web de NIMA Madrid.
    Devuelve un diccionario con los datos de la sede y del centro.
    """
    # Datos del EMA (empresa)
    datos_empresa = {
        "nif": webFunctions.leer_texto_por_campo(driver, "NIF:"),
        "nombre_empresa": webFunctions.leer_texto_por_campo(driver, "Razón Social:"),
        "direccion_empresa": webFunctions.leer_texto_por_campo(driver, "Dirección Sede:"),
        "municipio_empresa": webFunctions.leer_texto_por_campo(driver, "Municipio:"),
        "codigo_ine_municipio_empresa": webFunctions.leer_texto_por_campo(driver, "Código INE Municipio:"),
        "cp_empresa": webFunctions.leer_texto_por_campo(driver, "CP:"),
        "provincia_empresa": webFunctions.leer_texto_por_campo(driver, "Provincia:"),
        "codigo_ine_provincia_empresa": webFunctions.leer_texto_por_campo(driver, "Código INE Provincia:"),
        "nombre_centro_empresa": webFunctions.leer_texto_por_campo(driver, "Denominación del Centro:")
    }

    # Datos del centro (usando el segundo elemento para cada campo)
    datos_centro = {
        "nima": webFunctions.leer_texto_por_campo(driver, "NIMA:"),
        "nombre_centro": webFunctions.leer_texto_por_campo(driver, "Denominación del Centro:"),
        "direccion_centro": webFunctions.leer_texto_por_campo(driver, "Dirección Centro:"),
        "municipio_centro": webFunctions.leer_texto_por_campo_indice(driver, "Municipio:", indice=1),
        "codigo_ine_municipio_centro": webFunctions.leer_texto_por_campo_indice(driver, "Código INE Municipio:", indice=1),
        "cp_centro": webFunctions.leer_texto_por_campo_indice(driver, "CP:", indice=1),
        "provincia_centro": webFunctions.leer_texto_por_campo_indice(driver, "Provincia:", indice=1),
        "codigo_ine_provincia_centro": webFunctions.leer_texto_por_campo_indice(driver, "Código INE Provincia:", indice=1)
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

    # Buscar y hacer click en el enlace <a> con onclick="buscar('form');"
    webFunctions.clickar_enlace_por_onclick(driver, "buscar('form');")

    empresa = None
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
            try:
                boton = webFunctions.encontrar_elemento(
                    driver,
                    webFunctions.By.XPATH,
                    f"//input[@type='button' and @value='Consultar' and @onclick=\"{onclick}\"]"
                )
                if boton:
                    boton.click()
                    try:
                        datos_centro = extraer_datos_madrid(driver)
                        if datos_centro:
                            if empresa is None and "empresa" in datos_centro:
                                empresa = datos_centro["empresa"]
                            if "centro" in datos_centro:
                                centros.append(datos_centro["centro"])
                    except Exception as e:
                        logging.error(f"ERROR: No se han podido extraer los datos del centro en Madrid: {e}")
                    driver.back()
                else:
                    logging.warning("No se encontró el botón 'Consultar' para el onclick esperado.")
            except Exception as e:
                logging.error(f"ERROR: No se pudo encontrar o hacer click en el botón 'Consultar': {e}")
    except Exception as e:
        logging.error(f"ERROR: No se han podido procesar los centros asociados en Madrid para el NIF {nif}. Excepción: {e}")
    driver.quit()

    if empresa and centros:
        return {
            "empresa": empresa,
            "centros": centros
        }
    else:
        return None

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
    Lanza mensajes de error claros y evita mostrar stacktraces de Selenium.
    """
    logging.info(f"Buscando NIF: {nif}")
    selector_nif = f"//div[contains(@class, 'col-xs-4') and b[normalize-space(text())='Nif:'] and contains(., '{nif}')]"
    try:
        webFunctions.esperar_elemento(driver, "xpath", selector_nif)
        logging.info("Elemento NIF encontrado")
    except Exception as e:
        mensaje = str(e).splitlines()[0] if str(e) else repr(e)
        logging.error(f"No se encontró el elemento NIF para el NIF {nif}: {mensaje}")
        return None

    # Extraer NIF
    valor_nif = None
    try:
        texto_div_nif = webFunctions.esperar_y_obtener_texto(driver, "xpath", selector_nif)
        valor_nif = texto_div_nif.split("Nif:")[-1].strip() if "Nif:" in texto_div_nif else None
    except Exception as e:
        logging.error(f"Error extrayendo NIF del div: {e}")

    selector_nima = "//div[contains(@class, 'col-xs-4') and b[normalize-space(text())='Nima:']]"
    nima = None
    try:
        texto_div_nima = webFunctions.esperar_y_obtener_texto(driver, "xpath", selector_nima)
        nima = texto_div_nima.split("Nima:")[-1].strip() if "Nima:" in texto_div_nima else None
    except Exception as e:
        logging.error(f"Error extrayendo NIMA: {e}")

    selector_razon = "//div[contains(@class, 'col-xs-8') and b[normalize-space(text())='Raó social:']]"
    nombre_centro = None

    try:
        texto_div_razon = webFunctions.esperar_y_obtener_texto(driver, "xpath", selector_razon)
        if "Raó social:" in texto_div_razon:
            nombre_centro = texto_div_razon.split("Raó social:")[-1].strip()
            nombre_centro = " ".join(nombre_centro.split())
    except Exception as e:
        logging.error(f"Error extrayendo Razón Social: {e}")

    # Extraer todos los centros de la tabla
    selector_trs = "//tr[contains(@class, 'llistaopen1') or contains(@class, 'llistaopen2')]"
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

    # Si no hay datos relevantes, devuelve None
    if not (valor_nif or nima or nombre_centro or centros):
        logging.error(f"No se han encontrado datos relevantes para el NIF {nif} en Cataluña.")
        return None

    return {
        "nif": valor_nif,
        "nima": nima,
        "nombre_centro": nombre_centro,
        "centros": centros
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