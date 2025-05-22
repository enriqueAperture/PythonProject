from fastapi import FastAPI, HTTPException, Body
import logging
import mainNimaVlc

app = FastAPI()

def automation_nima_task(nif: str):
    """
    Tarea en segundo plano que ejecuta la automatización de Nima/VLC usando el nif recibido.
    """
    try:
        result = mainNimaVlc.run_main_nima_vlc(nif)
        logging.info(f"Automatización Nima/VLC completada: {result}")
    except Exception as e:
        logging.error(f"Error en automation_nima_task: {e}")

@app.post("/run-main-nima-vlc")
async def run_main_nima_vlc_endpoint(
    nif: str = Body(..., media_type="text/plain")
):
    """
    Endpoint para ejecutar la automatización Nima/VLC usando el nif recibido en formato texto plano
    y devolver el JSON que retorna la función run_main_nima_vlc.

    Ejemplo de llamada:
      POST /run-main-nima-vlc
      Body: B98969264
    """
    try:
        result = mainNimaVlc.run_main_nima_vlc(nif)
        return result
    except Exception as e:
        logging.error(f"Error al iniciar la automatización Nima/VLC: {e}")
        raise HTTPException(status_code=500, detail="Error interno en la automatización Nima/VLC")
