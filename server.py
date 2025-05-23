"""
HOWTO:
Para iniciar el servidor FastAPI, ejecuta el siguiente comando en la terminal:
    uvicorn server:app --reload --host 0.0.0.0 --port 8000 --log-level info

Ejemplo de uso del endpoint "busqueda-nima" mediante curl.exe:
    curl.exe -X POST "http://<IP_DEL_SERVIDOR>:8000/busqueda-nima" -H "Content-Type: text/plain" -d "B98969264"
"""

from fastapi import FastAPI, HTTPException, Body
import logging
import mainNima

app = FastAPI()

@app.post("/busqueda-nima")
async def busqueda_nima_endpoint(
    nif: str = Body(..., media_type="text/plain")
):
    """
    Endpoint para buscar el NIF en la web de NIMA y devolver el JSON extraído.

    Ejemplo de llamada:
      POST /busqueda-nima
      Body: B98969264

    Si ocurre alguna excepción en busqueda_NIMA o sus subfunciones, se devolverá un error HTTP con el mensaje.
    """
    try:
        resultado = mainNima.busqueda_NIMA(nif)
        return resultado
    except Exception as e:
        logging.error(f"Error en busqueda_nima_endpoint: {e}")
        # Puedes elegir otro código HTTP si lo prefieres, aquí usamos 400 en caso de error de búsqueda.
        raise HTTPException(status_code=400, detail=str(e))
