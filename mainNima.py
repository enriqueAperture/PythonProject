import loggerConfig
import logging
import nimaFunctions

# Pruebas para un NIF específico
NIF_PRUEBA = "B43693274" # Es de Metalls Aldaia
NIF_MADRID = "B88218938" # Es de Madrid
NIF_VALENCIA = "B98969264" # Es de Valencia
NIF_AUTONOMO = "27368619E" # Es de un autónomo
NIF_CATALUÑA = "B43659549" # Es de Cataluña

def busqueda_NIMA(nif):
    """
    Función principal para buscar el NIF en la web de NIMA según la comunidad autónoma.
    Si el NIF es de empresa, busca solo en la comunidad correspondiente.
    Si no es de empresa, busca en todas las comunidades y devuelve el primer resultado encontrado.
    Devuelve los datos en JSON.
    """
    if not nif:
        logging.error("NIF no válido")
        return None

    # Si es empresa (primer carácter es letra)
    if nif[0].isalpha():
        comunidad = nimaFunctions.obtener_comunidad_por_nif_empresas(nif)
        if comunidad == "Valencia":
            return nimaFunctions.busqueda_NIMA_Valencia(nif)
        elif comunidad == "Madrid":
            return nimaFunctions.busqueda_NIMA_Madrid(nif)
        elif comunidad == "Castilla":
            return nimaFunctions.busqueda_NIMA_Castilla(nif)
        elif comunidad == "Cataluña":
            return nimaFunctions.busqueda_NIMA_Cataluña(nif)
        else:
            logging.error(f"Comunidad no válida o NIF no reconocido: {comunidad}")
            return None
    else:
        # No es empresa: probar en todas las comunidades
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
    
datos_json = busqueda_NIMA(NIF_CATALUÑA)
print(datos_json)