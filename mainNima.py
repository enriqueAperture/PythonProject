from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import nimaFunctions

NIF_PRUEBA = "B43693274"
NIF_MADRID = "B88218938"

#datos_json = nimaFunctions.busqueda_NIMA_Valencia(NIF_PRUEBA)
#datos_json = nimaFunctions.busqueda_NIMA_Madrid(NIF_MADRID)
datos_json = nimaFunctions.busqueda_NIMA_Castilla(NIF_PRUEBA)

print(datos_json)