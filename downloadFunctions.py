import logging
from config import BASE_DIR
import loggerConfig
import os
import json
import time
from selenium import webdriver

import webConfiguration
import webFunctions

WEB = "https://ash-speed.hetzner.com/"

def ensure_download_path(path: str) -> str:
    """Crea el directorio si no existe y devuelve la ruta absoluta."""
    os.makedirs(path, exist_ok=True)
    return os.path.abspath(path)

def configure_driver_download_path(driver: webdriver.Chrome, download_path: str):
    """Configura un driver existente para descargar en el path dado."""
    params = {
        "cmd": "Page.setDownloadBehavior",
        "params": {
            "behavior": "allow",
            "downloadPath": os.path.abspath(download_path)
        }
    }
    driver.execute_cdp_cmd("Page.setDownloadBehavior", params["params"])

def snapshot_folder_state(path: str) -> dict:
    """Guarda el estado actual de los archivos en el directorio."""
    files = os.listdir(path)
    state = {
        "path": os.path.abspath(path),
        "files": sorted(files)
    }
    return state

def save_snapshot(snapshot: dict, filename: str):
    """Guarda el snapshot en un JSON."""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(snapshot, f, indent=4)

def load_snapshot(filename: str) -> dict:
    """Carga un snapshot desde un JSON."""
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

def detect_new_file(old_state: dict, new_state: dict) -> str | None:
    """Devuelve el nombre del archivo nuevo si lo hay (ignorando crdownload)."""
    old_files = set(old_state["files"])
    new_files = set(f for f in new_state["files"] if not f.endswith('.crdownload') and not f.endswith('.htm'))
    new_entries = new_files - old_files
    return next(iter(new_entries), None)

def wait_for_new_download(download_path: str, old_state: dict, num_descargas: int = 1, timeout: int = 7200) -> list:
    """
    Espera hasta detectar el número de archivos nuevos indicados (ignorando .crdownload y .htm) o agotar el tiempo.
    Devuelve la lista de nombres de archivos nuevos detectados.
    """
    archivos_detectados = set()
    for _ in range(timeout):
        time.sleep(1)
        new_state = snapshot_folder_state(download_path)
        nuevos = set(f for f in new_state["files"] if not f.endswith('.crdownload') and not f.endswith('.htm')) - set(old_state["files"])
        archivos_detectados.update(nuevos)
        if len(archivos_detectados) >= num_descargas:
            for archivo in archivos_detectados:
                logging.info(f"Archivo nuevo detectado: {archivo}")
            return list(archivos_detectados)
    logging.error(f"No se detectaron todas las descargas esperadas ({num_descargas}). Solo detectados: {len(archivos_detectados)}")

# ------------------- FUNCIONES REUTILIZABLES PARA OTROS SCRIPTS -------------------

def setup_descarga(driver: webdriver.Chrome, folder_name: str = "") -> str:
    """
    Prepara el entorno de descargas para Selenium.
    Crea la carpeta BASE_DIR/descargas_temporales/[folder_name] y configura el driver para descargar ahí.
    Devuelve la ruta absoluta de la carpeta de descargas.
    """
    base_download_folder = os.path.join(BASE_DIR, "descargas_temporales")
    if folder_name:
        download_path = os.path.join(base_download_folder, folder_name)
    else:
        download_path = base_download_folder
    download_path = ensure_download_path(download_path)
    configure_driver_download_path(driver, download_path)
    logging.info(f"Descargas configuradas en: {download_path}")
    return download_path

def finalizar_descarga(driver: webdriver.Chrome):
    """
    Limpia la configuración de descargas si es necesario y permite continuar con el flujo Selenium.
    Actualmente solo cierra el driver, pero se puede ampliar si se requiere lógica adicional.
    """
    driver.quit()
    logging.info("Driver cerrado tras la descarga.")
