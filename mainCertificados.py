"""
Módulo: mainCertificados.py

Este módulo orquesta el flujo de automatización para la gestión de certificados en la web de MITECO,
utilizando Selenium para interactuar con la interfaz web y uiautomation junto con funciones auxiliares
de autoFirmaHandler y certHandler para la selección del certificado a utilizar (por DNIe o certificado electrónico).

Flujo general:
  1. Procesa todos los archivos XML de la carpeta /input uno a uno.
  2. Para cada XML, ejecuta el flujo de automatización y mueve el XML procesado a /trash/{nombre_productor}.
  3. Cuando no quedan XML, mueve el PDF a la carpeta del último {nombre_productor} en /trash y termina.

Ejemplo de uso:
    Ejecutar este script inicia el flujo de automatización para el proceso de certificados en MITECO.
    Al finalizar, se cierra el navegador.
"""

import os
import time
import shutil
import autoFirmaHandler
import certHandler
import extraerXMLE3L
import loggerConfig
import logging
import webConfiguration
import webFunctions
from config import BASE_DIR, cargar_variables

# URL y configuraciones
WEB_MITECO = ("https://sede.miteco.gob.es/portal/site/seMITECO/login?"
              "urlLoginRedirect=L3BvcnRhbC9zaXRlL3NlTUlURUNPL3BvcnRsZXRfYnVzP2lkX3Byb2NlZGltaWVudG89NzM2"
              "JmlkZW50aWZpY2Fkb3JfcGFzbz1QUkVJTklDSU8mc3ViX29yZ2Fubz0xMSZwcmV2aW9fbG9naW49MQ==")
INPUT_DIR = os.path.join(BASE_DIR, "input")
TRASH_DIR = os.path.join(BASE_DIR, "trash")
PDF_FILE = os.path.join(INPUT_DIR, "acuerdo-29-5-2025-JOSE FERNANDO PEREZ .pdf")
INFO_CERTS = os.path.join(BASE_DIR, "data", "informacionCerts.txt")
info = cargar_variables(INFO_CERTS)

def get_linkMiteco(regage_val, nif_productor, nif_representante):
      linkMiteco = (
         "https://sede.miteco.gob.es/portal/site/seMITECO/area_personal"
         "?btnDetalleProc=btnDetalleProc"
         "&pagina=1"
         f"&idExpediente={regage_val}"
         "&idProcedimiento=736"
         "&idSubOrganoResp=11"
         f"&idDocIdentificativo={nif_productor}"
         f"&idDocRepresentante={nif_representante}"
         "&idEstadoSeleccionado=-1"
         "&idTipoProcSeleccionado=EN+REPRESENTACION+(CERTIFICADO)"
         f"&regInicial={regage_val}"
         "&numPagSolSelec=10#no-back-button"
      )
      return linkMiteco
def abrir_link_miteco_con_json(driver, json_result):
      """
      Abre el enlace de MITECO generado a partir de los datos de json_result.
      """
      regage_val = json_result.get("regage", "")
      nif_productor = json_result.get("nif_productor", "")
      nif_representante = json_result.get("nif_representante", "")

      linkMiteco = get_linkMiteco(regage_val, nif_productor, nif_representante)

      logging.info(f"Abrir enlace MITECO: {linkMiteco}")
      webFunctions.abrir_web(driver, linkMiteco)
      time.sleep(30)

def mover_a_trash(origen, nombre_productor):
    destino_dir = os.path.join(TRASH_DIR, nombre_productor)
    os.makedirs(destino_dir, exist_ok=True)
    destino = os.path.join(destino_dir, os.path.basename(origen))
    shutil.move(origen, destino)
    logging.info(f"Archivo '{os.path.basename(origen)}' movido a '{destino_dir}'.")

def procesar_xml(xml_path):
    logging.info(f"--- Procesando archivo XML: {os.path.basename(xml_path)} ---")
    # Configurar el driver de Selenium
    driver = webConfiguration.configure()

    # Abrir la web de MITECO
    webFunctions.abrir_web(driver, WEB_MITECO)
    webFunctions.esperar_elemento_por_id(driver, "breadcrumb")

    # Proceso de autenticación y selección de acceso
    webFunctions.clickar_boton_por_value(driver, "acceder")
    webFunctions.clickar_boton_por_texto(driver, "Acceso DNIe / Certificado electrónico")

    # Selección del certificado (utiliza certHandler para buscar y confirmar el certificado deseado)
    certHandler.seleccionar_certificado_chrome(info.get("NOMBRE_CERT"))

    # Espera a que la página principal del formulario cargue
    webFunctions.esperar_elemento_por_id(driver, "wrapper", timeout=15)

    # Rellenar los datos del formulario
    webFunctions.escribir_en_elemento_por_id(driver, "id_direccion", info.get("DIRECCION"))
    webFunctions.seleccionar_elemento_por_id(driver, "id_pais", info.get("PAIS"))
    webFunctions.seleccionar_elemento_por_id(driver, "id_provincia", info.get("PROVINCIA"))
    webFunctions.seleccionar_elemento_por_id(driver, "id_municipio", info.get("MUNICIPIO"))
    webFunctions.escribir_en_elemento_por_id(driver, "id_codigo_postal", info.get("CODIGO_POSTAL"))
    webFunctions.escribir_en_elemento_por_id(driver, "id_correo_electronico", info.get("CORREO_ELECTRONICO"))

    # Enviar el formulario
    webFunctions.clickar_boton_por_id(driver, "btnForm")
    time.sleep(5)

    # Seleccionar el método de envío de datos
    webFunctions.clickar_boton_por_id(driver, "tipoEnvioNtA")
    webFunctions.escribir_en_elemento_por_id(driver, "file", xml_path)

    # Continuar con el proceso de autenticación y firma
    webFunctions.clickar_boton_por_clase(driver, "loginBtn")
    webFunctions.clickar_boton_por_texto(driver, "Continuar")
    webFunctions.escribir_en_elemento_por_id(driver, "idFichero", PDF_FILE)
    webFunctions.clickar_boton_por_id(driver, "btnForm")
    webFunctions.clickar_boton_por_id(driver, "bSiguiente")
    webFunctions.clickar_boton_por_id(driver, "idFirmarRegistrar")
    time.sleep(2)
    webFunctions.clickar_boton_por_id(driver, "idFirmarRegistrar")

    # Ejecutar el proceso de firma mediante AutoFirma
    autoFirmaHandler.firmar_en_autofirma()

    regage = webFunctions.obtener_texto_por_parte(driver, "Descargar Justificante:").split()[-1]
    logging.info(f"Código de justificante obtenido: {regage}")

    json_result = extraerXMLE3L.extraer_info_xml(xml_path, regage)
    logging.info(f"Información extraída del XML: {json_result}")

   

    # Cerrar el navegador
    driver.quit()
    return json_result

def main():
    # Obtener todos los archivos XML ordenados
    xml_files = sorted([os.path.join(INPUT_DIR, f) for f in os.listdir(INPUT_DIR) if f.lower().endswith('.xml')])
    ultimo_nombre_productor = None
    fallidos = []

    while xml_files:
        procesados_esta_vuelta = []
        for xml_file in xml_files:
            try:
                resultado = procesar_xml(xml_file)
                nombre_productor = resultado.get("nombre_productor", "desconocido").replace(" ", "_")
                mover_a_trash(xml_file, nombre_productor)
                ultimo_nombre_productor = nombre_productor
                procesados_esta_vuelta.append(xml_file)
            except Exception as e:
                logging.error(f"Error procesando '{os.path.basename(xml_file)}': {e}")
                # No mover el archivo, se queda en input para el siguiente intento

        # Actualizar la lista de archivos xml para la siguiente vuelta (solo los que no se han procesado)
        xml_files = sorted([os.path.join(INPUT_DIR, f) for f in os.listdir(INPUT_DIR) if f.lower().endswith('.xml')])

        # Si no se ha procesado ningún archivo en esta vuelta, salir para evitar bucle infinito
        if not procesados_esta_vuelta and xml_files:
            logging.error("No se ha podido procesar ninguno de los archivos XML restantes. Revisa los archivos en /input.")
            break

    # Cuando no quedan XML, mover el PDF a la carpeta del último productor
    if ultimo_nombre_productor and os.path.exists(PDF_FILE):
        logging.info(f"Moviendo PDF '{os.path.basename(PDF_FILE)}' a la carpeta '{ultimo_nombre_productor}' en trash.")
        mover_a_trash(PDF_FILE, ultimo_nombre_productor)
    logging.info("Proceso completado. Todos los archivos procesados y movidos.")

if __name__ == "__main__":
    main()