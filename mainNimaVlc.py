"""
mainNimaVlc.py
Este script automatiza la extracción de datos de una empresa y su centro asociado desde la web de residuos de la Generalitat Valenciana (https://residuos.gva.es/RES_BUSCAWEB/buscador_residuos_avanzado.aspx).
Utiliza Selenium para interactuar con la web, buscar por NIF, navegar por los resultados y extraer información relevante, que posteriormente se guarda en un archivo JSON.
Flujo principal:
- Configura el driver web.
- Accede a la web y realiza una búsqueda por NIF.
- Accede al detalle del gestor encontrado.
- Extrae datos de la empresa, centro y códigos de residuos.
- Guarda los datos extraídos en un archivo JSON.
Dependencias:
- loggerConfig: Configuración del logging.
- logging: Registro de eventos.
- webConfiguration: Configuración del driver Selenium.
- webFunctions: Funciones auxiliares para interactuar con la web.
- json: Para guardar los datos extraídos en formato JSON.
El archivo generado 'datos_empresa.json' contendrá la información estructurada de la empresa y su centro.
"""
import loggerConfig
import logging
import webConfiguration
import webFunctions
import json

WEB_NIMA_VLC = "https://residuos.gva.es/RES_BUSCAWEB/buscador_residuos_avanzado.aspx"
NIF = "B98969264"

def run_main_nima_vlc(nif: str) -> dict:
    """
    Ejecuta la automatización y devuelve el resultado.
    """
    driver = webConfiguration.configure()
    try:
        logging.info(f"Abriendo la web: {WEB_NIMA_VLC}")
        webFunctions.abrir_web(driver, WEB_NIMA_VLC)

        logging.info("Escribiendo NIF en el input")
        webFunctions.escribir_en_elemento_por_id(driver, "ctl00_ContentPlaceHolder1_txtNIF", nif)

        logging.info("Haciendo click en el botón Buscar")
        webFunctions.clickar_boton_por_id(driver, "ctl00_ContentPlaceHolder1_btBuscar")

        logging.info("Abriendo el enlace del gestor encontrado")
        webFunctions.abrir_link_por_boton_id(driver, "ctl00_ContentPlaceHolder1_gvResultados_ctl03_hypGestor")
    
        logging.info("Extrayendo datos de la empresa")
        nombre_empresa = webFunctions.obtener_texto_elemento_por_id(driver, "NOMBREEMPRESA1-0")
        nif_val = webFunctions.obtener_texto_elemento_por_id(driver, "ENIF1-0")
        direccion = webFunctions.obtener_texto_elemento_por_id(driver, "EDIRECCION1-0")
        codigo_postal = webFunctions.obtener_texto_elemento_por_id(driver, "ECODIPOS1-0")
        localidad_provincia_empresa = webFunctions.obtener_texto_elemento_por_id(driver, "Text8-0")
        telefono = webFunctions.obtener_texto_elemento_por_id(driver, "ETELEFONO1-0")

        logging.info("Extrayendo datos del centro")
        nombre_centro = webFunctions.obtener_texto_elemento_por_id(driver, "NOMBRECENTRO1-0-0")
        nima = webFunctions.obtener_texto_elemento_por_id(driver, "FCENCODCENTRO1-0-0")
        direccion_centro = webFunctions.obtener_texto_elemento_por_id(driver, "FDIRECCION1-0-0")
        localidad_provincia_centro = webFunctions.obtener_texto_elemento_por_id(driver, "Text7-0-0")
        codigo_ine = webFunctions.obtener_texto_elemento_por_id(driver, "FCODINE1-0-0")
        telefono_centro = webFunctions.obtener_texto_elemento_por_id(driver, "FTELEFONO1-0-0")
        codigo_residuo_1 = webFunctions.obtener_texto_elemento_por_id(driver, "Text10-0-0-0").split()[0]
        codigo_residuo_2 = webFunctions.obtener_texto_elemento_por_id(driver, "Text10-0-0-1").split()[0]
    
        data = {
            "nombre_empresa": nombre_empresa,
            "nif": nif_val,
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
    
        logging.info("Datos de la empresa encontrados y extraídos correctamente.")
        return data
    except Exception as e:
        logging.error(f"Error en la automatización Nima/VLC: {e}")
        raise
    finally:
        if driver:
            logging.info("Cerrando el navegador.")
            driver.quit()

