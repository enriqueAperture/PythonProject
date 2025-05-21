import nimaFunctions
import pandas as pd
import json

# Pruebas para un NIF específico
NIF_PRUEBA = "B43693274" # Es de Toledo
NIF_MADRID = "B88218938" # Es de Madrid
NIF_VALENCIA = "B98969264" # Es de Valencia

datos_json = nimaFunctions.busqueda_NIMA_Valencia("B98670615")
#datos_json = nimaFunctions.busqueda_NIMA_Madrid("B87148078")
#datos_json = nimaFunctions.busqueda_NIMA_Castilla("E45879897")

print(datos_json)


# ##PRUEBAS PARA UNA LISTA DE NIFS
# # Leer la columna 'cif_recogida' del Excel
# ruta_excel = r"C:\Users\Usuario\Desktop\PYTHON\EXCELS\excel_recogidas.xls"
# df = pd.read_excel(ruta_excel)
# lista_nifs = df['cif_recogida'].dropna().unique()

# # Procesar cada NIF y guardar los resultados en una lista
# resultados = []
# for nif in lista_nifs:
#     datos_json = nimaFunctions.busqueda_NIMA_Madrid(str(nif))
#     print(datos_json)
#     resultados.append(datos_json)

# # Si quieres guardar todos los resultados en un archivo JSON:

# with open("resultados_nima_castilla.json", "w", encoding="utf-8") as f:
#     json.dump(resultados, f, ensure_ascii=False, indent=4)

# print(resultados)
