"""
HOWTO:
Para iniciar el servidor FastAPI, ejecuta el siguiente comando en la terminal:
    uvicorn server:app --reload --host 0.0.0.0 --port 8000 --reload --log-level info

Ejemplo de uso del endpoint "busqueda-nima" mediante curl.exe:
    curl.exe -X POST "http://localhost:8000/busqueda-nima" -H "Content-Type: text/plain" -d "B98969264"
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

    Si busqueda_NIMA devuelve None se levantará un error 400.
    """
    try:
        resultado = mainNima.busqueda_NIMA(nif)
        if resultado is None:
            raise HTTPException(status_code=400, detail="No se ha encontrado nada por ese NIF")
        return resultado
    except HTTPException as http_err:
        raise http_err
    except Exception as e:
        logging.error(f"Error en busqueda_nima_endpoint: {e}")
        raise HTTPException(status_code=500, detail="Error interno al procesar la búsqueda")
