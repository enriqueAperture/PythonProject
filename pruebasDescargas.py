import logging
from config import BASE_DIR
import loggerConfig
import os
import json
import time
import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

import webConfiguration
import webFunctions


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


def wait_for_new_download(download_path: str, old_state: dict, timeout: int = 7200) -> bool:
    """Espera hasta detectar un nuevo archivo o agotar el tiempo."""
    for _ in range(timeout):
        time.sleep(1)
        new_state = snapshot_folder_state(download_path)
        new_file = detect_new_file(old_state, new_state)
        if new_file:
            logging.info(f"Archivo nuevo detectado: {new_file}")
            return True
    logging.error("No se detectó ninguna descarga nueva.")
    return False


def main():
    # Crear la carpeta de descargas en base_dir
    download_folder = os.path.join(BASE_DIR, "descargas_temporales")
    download_path = ensure_download_path(download_folder)

    # Crear la carpeta "temp" para guardar el snapshot
    temp_folder = os.path.join(BASE_DIR, "temp")
    temp_folder = ensure_download_path(temp_folder)
    snapshot_filename = os.path.join(temp_folder, "snapshot.json")

    # Paso 1: Guardar estado inicial (de la carpeta de descargas)
    old_state = snapshot_folder_state(download_path)
    save_snapshot(old_state, snapshot_filename)

    # Paso 2: Preparar el navegador
    driver = webConfiguration.configure()
    configure_driver_download_path(driver, download_path)
    logging.info("Navegador preparado. Ejecuta tu script de descarga ahora.")

    # Paso 3: Esperar nueva descarga
    # Se carga el snapshot de la carpeta "temp"
    old_state = load_snapshot(snapshot_filename)
    webFunctions.abrir_web(driver, "https://ash-speed.hetzner.com/")
    webFunctions.clickar_boton_por_link(driver, "1GB.bin")
    success = wait_for_new_download(download_path, old_state)

    # Cierre
    driver.quit()
    return success


if __name__ == "__main__":
    resultado = main()
    logging.info(f"\nResultado: {' Descarga detectada' if resultado else 'No se detectó nada'}")

