import nimaFunctions

# Pruebas para un NIF específico
NIF_PRUEBA = "B43693274" # Es de Metalls Aldaia
NIF_MADRID = "B88218938" # Es de Madrid
NIF_VALENCIA = "B98969264" # Es de Valencia

datos_json = nimaFunctions.busqueda_NIMA(NIF_VALENCIA)

print(datos_json)
