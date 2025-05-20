import time

import certHandler
import loggerConfig
import logging
import webConfiguration
import webFunctions
import pandas as pd
import json

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import nimaFunctions

NIF_PRUEBA = "B43693274"

driver = webConfiguration.configure()

nimaFunctions.busqueda_NIMA_Valencia(NIF_PRUEBA)

# Imprimir la URL actual de la página
print(f"URL actual: {driver.current_url}")

# Suponiendo que se puede leer los elementos de la página

# Leer el nombre EMA por clase
#nombre_EMA = webFunctions.leer_texto_por_clase(driver, "fc11e6244e-a63b-4604-bd06-09e4ba092119-2")

# clase_repetido = fc6bfe381c-75c3-414f-b7d8-ad64ac4f5d3f-1

# Leer el NIF EMA por clase
# nif_EMA = webFunctions.leer_texto_por_clase(driver, "fc6bfe381c-75c3-414f-b7d8-ad64ac4f5d3f-1")

# Leer la dirección EMA por clase
# direccion_EMA = webFunctions.leer_texto_por_clase(driver, "fc6bfe381c-75c3-414f-b7d8-ad64ac4f5d3f-1")

# Leer el codigo postal EMA por clase
# cp_EMA = webFunctions.leer_texto_por_clase(driver, "fc6bfe381c-75c3-414f-b7d8-ad64ac4f5d3f-1")

# Leer el municipio EMA por clase
# municipio_EMA = webFunctions.leer_texto_por_clase(driver, "fc6bfe381c-75c3-414f-b7d8-ad64ac4f5d3f-1")

# Leer la provincia EMA por clase
# provincia_EMA = webFunctions.leer_texto_por_clase(driver, "fc6bfe381c-75c3-414f-b7d8-ad64ac4f5d3f-1")

# Leer el telefono EMA por clase
# telefono_EMA = webFunctions.leer_texto_por_clase(driver, "fc6bfe381c-75c3-414f-b7d8-ad64ac4f5d3f-1")

# Leer el fax EMA por clase
# fax_EMA = webFunctions.leer_texto_por_clase(driver, "fcd719fddc-ce38-4993-ae65-16ac02f2644c-1")

# Leer el nombre del centro por clase
# nombre_centro = webFunctions.leer_texto_por_clase(driver, "fcd719fddc-ce38-4993-ae65-16ac02f2644c-2")

# Leer el codigo NIMA por clase
# codigo_NIMA = webFunctions.leer_texto_por_clase(driver, "fcd719fddc-ce38-4993-ae65-16ac02f2644c-1")

# Leer la direccion del centro por clase
# direccion_centro = webFunctions.leer_texto_por_clase(driver, "fcd719fddc-ce38-4993-ae65-16ac02f2644c-1")

# Leer el codigo postal del centro por clase
# cp_centro = webFunctions.leer_texto_por_clase(driver, "fcd719fddc-ce38-4993-ae65-16ac02f2644c-1")

# Leer el municipio del centro por clase
# municipio_centro = webFunctions.leer_texto_por_clase(driver, "fcd719fddc-ce38-4993-ae65-16ac02f2644c-1")

# Leer el codigo INE del municipio por clase
# codigo_INE_municipio = webFunctions.leer_texto_por_clase(driver, "fcd719fddc-ce38-4993-ae65-16ac02f2644c-1")

# Leer el telefono del centro por clase
# telefono_centro = webFunctions.leer_texto_por_clase(driver, "fcd719fddc-ce38-4993-ae65-16ac02f2644c-1")

# Leer el fax del centro por clase
# fax_centro = webFunctions.leer_texto_por_clase(driver, "fcd719fddc-ce38-4993-ae65-16ac02f2644c-1")

time.sleep(5)

"""
CAMPOS PARA LA LECTURA EN JSON
nombre_EMA ->
NIF_EMA
direccion_EMA
cp_EMA
municipio_EMA
provincia_EMA
telefono_EMA
fax_EMA
nombre_centro
codigo_NIMA
direccion_centro
cp_centro
municipio_centro
codigo_INE_municipio
telefono_centro
fax_centro
RESTO
"""