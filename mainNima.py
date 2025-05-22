import loggerConfig
import logging
import nimaFunctions

# Pruebas para un NIF específico
NIF_PRUEBA = "B43693274" # Es de Metalls Aldaia
NIF_MADRID = "B88218938" # Es de Madrid
NIF_VALENCIA = "B98969264" # Es de Valencia
NIF_AUTONOMO = "27368619E" # Es de un autónomo

def busqueda_NIMA(NIF):
    """
    Función principal para buscar el NIF en la web de NIMA según la comunidad autónoma.
    Detecta la comunidad usando obtener_comunidad_por_nif y llama a la función correspondiente.
    Devuelve los datos en JSON.
    """
    try:
        comunidad = nimaFunctions.obtener_comunidad_por_nif(NIF)
        if comunidad == "Valencia":
            return nimaFunctions.busqueda_NIMA_Valencia(NIF)
        elif comunidad == "Madrid":
            return nimaFunctions.busqueda_NIMA_Madrid(NIF)
        elif comunidad == "Castilla":
            return nimaFunctions.busqueda_NIMA_Castilla(NIF)
        else:
            logging.error(f"Comunidad no válida o NIF no reconocido: {comunidad}")
            return None
    except Exception as e:
        logging.error(f"Error en busqueda_NIMA: {e}")
        return None
