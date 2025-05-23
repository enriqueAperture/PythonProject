import loggerConfig
import logging
import nimaFunctions

def busqueda_NIMA(nif):
    """
    Toma el nif y busca en las diferentes comunidades autónomas en el orden:
    Valencia, Madrid, Castilla, Cataluña.
    Devuelve un JSON con los datos o lanza una excepción con mensaje descriptivo.
    """
    if not nif:
        logging.error("NIF no válido")
        raise ValueError("NIF no válido")
    
    errores = []  # Para acumular los mensajes de error de cada intento
    for funcion_busqueda in [nimaFunctions.busqueda_NIMA_Valencia,
                             nimaFunctions.busqueda_NIMA_Madrid,
                             nimaFunctions.busqueda_NIMA_Castilla,
                             nimaFunctions.busqueda_NIMA_Cataluña]:
        try:
            resultado = funcion_busqueda(nif)
            if resultado:
                return resultado
        except Exception as e:
            mensaje = f"{funcion_busqueda.__name__}: {e}"
            logging.info(f"No encontrado en {funcion_busqueda.__name__}: {e}")
            errores.append(mensaje)
    error_msg = "NIF no encontrado en ninguna comunidad. Detalles: " + "; ".join(errores)
    logging.error(error_msg)
    raise Exception(error_msg)
