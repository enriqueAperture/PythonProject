import logging
import nimaFunctions

def busqueda_NIMA(nif):
    """
    Toma el nif y busca en las diferentes comunidades autónomas en el orden siguiente: Valencia, Madrid, Castilla, Cataluña.
    Devuelve un JSON con los datos.
    """
    if not nif:
        logging.error("NIF no válido")
        return None

    for funcion_busqueda in [nimaFunctions.busqueda_NIMA_Valencia, nimaFunctions.busqueda_NIMA_Madrid,
                                nimaFunctions.busqueda_NIMA_Castilla, nimaFunctions.busqueda_NIMA_Cataluña]:
        try:
            resultado = funcion_busqueda(nif)
            if resultado:
                return resultado
        except Exception as e:
            logging.info(f"No encontrado en {funcion_busqueda.__name__}: {e}")
    logging.error("NIF no encontrado en ninguna comunidad")
    return None
