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

#datos_json = nimaFunctions.busqueda_NIMA_Valencia(NIF_PRUEBA)
#datos_json = nimaFunctions.busqueda_NIMA_Madrid(NIF_MADRID)
datos_json = nimaFunctions.busqueda_NIMA_Castilla(NIF_PRUEBA)

print(datos_json)
