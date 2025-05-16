import glob
import os
import time

import pandas
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import webFunctions

DOWNLOAD_DIR = os.path.join(os.path.expanduser("~"), "Downloads")
EXCEL_RECOGIDAS = r"C:\Users\Metalls1\Downloads\excel_recogidas.xls"

def _esperar_descarga(carpeta, extension=".xlsx", timeout=30):
    tiempo_inicio = time.time()
    while time.time() - tiempo_inicio < timeout:
        archivos = glob.glob(os.path.join(carpeta, f"*.{extension.lstrip('.')}"))
        if archivos:
            # Verifica que no estén en proceso (.crdownload)
            finalizados = [f for f in archivos if not f.endswith('.crdownload')]
            if finalizados:
                return finalizados[0]
        time.sleep(1)
    raise TimeoutError("Descarga no completada en el tiempo esperado.")

def _nif_no_encontrados_en_nubelus(cif_nubelus, datos_recogidas):

    filas_no_encontradas = []

    for idx, fila in datos_recogidas.iterrows():

        cif_valor = fila['cif_recogida']

        if cif_valor not in cif_nubelus.values:
            filas_no_encontradas.append(fila)

    return pandas.DataFrame(filas_no_encontradas)

def sacarEmpresasNoAñadidas(driver: webdriver.Chrome):
    try:
        archivo_xlsx = _esperar_descarga(DOWNLOAD_DIR)
        logging.info(f"Archivo descargado: {archivo_xlsx}")
    except TimeoutError as e:
        logging.error(e)
        driver.quit()
        exit()

    # Leemos los archivos excel
    entidades_medioambientales = pandas.read_excel(archivo_xlsx)
    excel_recogidas = pandas.read_excel(EXCEL_RECOGIDAS)

    ##Nos quedamos con la columna "NIF" del excel entidades_medioambientales
    cif_nubelus = entidades_medioambientales["NIF"]

    ##Nos quedamos solo con los datos que vamos a tratar del excel recogidas
    datos = excel_recogidas[[
        'cif_recogida', 'nombre_recogida', 'direccion_recogida', 'cp_recogida', 'poblacion_recogida', 'provincia_recogida', 'email_recogida', 'telf_recogida'
    ]]

    # Llamamos a la función y guardamos el resultado en la variable 'datos_no_encontrados'
    datos_no_encontrados = _nif_no_encontrados_en_nubelus(cif_nubelus, datos)

    return datos_no_encontrados

def añadirEmpresas(driver, empresas_añadir):
    """
    Itera sobre el DataFrame 'empresas_añadir' y realiza las acciones necesarias
    para añadir cada empresa en la aplicación web.
    
    Se asume que el botón para iniciar la acción de añadir empresas ya se ha clicado
    y que se encuentran visibles los campos de entrada correspondientes.
    """
    for idx, empresa in empresas_añadir.iterrows():
        try:
            logging.info(f"Añadiendo empresa: {empresa['nombre_recogida']}")
            webFunctions.clickar_boton_por_clase(driver, "miBoton.nuevo")
            # 1. Completar el campo Nombre
            webFunctions.esperar_elemento(driver, By.ID, "pDenominacion", timeout=10)
            webFunctions.escribir_en_elemento_por_id(driver, "pDenominacion", empresa["nombre_recogida"])

            # 2. Completar el campo CIF
            webFunctions.escribir_en_elemento_por_name(driver, "pNif", empresa["cif_recogida"])
            # 3. Completar el campo Fiscal
            webFunctions.seleccionar_elemento_por_nombre(driver, "pForma_fiscal", "Física")
            # 4. Completar el campo Nombre
            webFunctions.escribir_en_elemento_por_name(driver, "pNombre", str(empresa["nombre_recogida"]).split()[0])
            # 5. Completar el campo Apellidos
            webFunctions.escribir_en_elemento_por_name(driver, "pApellidos", " ".join(str(empresa["nombre_recogida"]).split()[1:]))
            # 4. Completar el campo Domicilio
            webFunctions.escribir_en_elemento_por_name(driver, "pDomicilio", empresa["direccion_recogida"])
            # 5. Completar el campo Municipio
            webFunctions.escribir_en_elemento_por_name(driver, "pDenominacion_ine_municipio", str(empresa["poblacion_recogida"]).rstrip())
            time.sleep(1)
            webFunctions.escribir_en_elemento_por_name(driver, "pDenominacion_ine_municipio", Keys.ENTER)
            # 6. Completar el campo Provincia
            webFunctions.escribir_en_elemento_por_name(driver, "pPoblacion", empresa["provincia_recogida"])
            # 7. Completar el campo CP
            webFunctions.escribir_en_elemento_por_name(driver, "pCodigoPostal", str(empresa["cp_recogida"]))
            # 8. Completar el campo Telefono
            webFunctions.escribir_en_elemento_por_name(driver, "pTelefono", str(empresa["telf_recogida"]))
            # 9. Completar el campo Email
            webFunctions.escribir_en_elemento_por_name(driver, "pEmail", empresa["email_recogida"])
            # 10. Confirmar la adición (clic en botón de aceptar o guardar)
            webFunctions.clickar_boton_por_clase(driver, "miBoton.cancelar")
            
            # Espera a que la acción se procese antes de continuar
            time.sleep(1)
        except Exception as error:
            logging.error(f"Error al añadir la empresa {empresas_añadir.iloc[0]['nombre_recogida']}: {error}")
