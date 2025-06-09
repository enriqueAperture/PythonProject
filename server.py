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
from pydantic import BaseModel
from config import BASE_DIR
from mainCertificados import procesar_xml  # se asume que esta función retorna un dict con el código "regage"
from linkRegage import get_linkMiteco
import os

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
# Modelo de datos de entrada
class RegageRequest(BaseModel):
    xml_content: str  # Contenido XML en formato string
    pdf_path: str     # Ruta al archivo PDF

@app.post("/obtener-link-regage")
async def obtener_link_regage(req: RegageRequest):
    try:
        # Crear carpeta temporal para almacenar el XML de entrada
        temp_dir = os.path.join(BASE_DIR, "temp")
        os.makedirs(temp_dir, exist_ok=True)
        temp_xml_path = os.path.join(temp_dir, "temp_input.xml")
        
        # Guardar el contenido XML en el archivo temporal
        with open(temp_xml_path, "w", encoding="utf-8") as f:
            f.write(req.xml_content)
        
        # Procesar el XML utilizando la función de mainCertificados (se espera que retorne un dict que incluya "regage")
        resultado = procesar_xml(temp_xml_path, req.pdf_path)
        if not resultado or "regage" not in resultado:
            raise Exception("No se pudo obtener el código regage a partir del XML.")
        regage_val = resultado["regage"]
        nif_productor = resultado["nif_productor"]
        nif_representante = resultado["nif_representante"]
        
        # Construir el enlace regage utilizando la función de linkRegage
        enlace = get_linkMiteco(regage_val, nif_productor, nif_representante)
        
        return {"link_regage": enlace}
    
    except Exception as e:
        logging.error(f"Error en /obtener-link-regage: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))
