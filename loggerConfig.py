import logging
import os
from datetime import datetime

# Crear carpetas si no existen
os.makedirs("logs", exist_ok=True)
os.makedirs("screenshots", exist_ok=True)

# Timestamp para el archivo de log
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
log_file = f"logs/selenium_log_{timestamp}.log"

# Crear logger raíz
logger = logging.getLogger()
logger.setLevel(logging.INFO)  # Tu nivel de log

# Limpiar handlers previos (por si se ejecuta varias veces en el mismo intérprete)
if logger.hasHandlers():
    logger.handlers.clear()

# Handler para archivo
file_handler = logging.FileHandler(log_file, encoding="utf-8")
file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))

# Handler para consola
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))

# Añadir handlers al logger raíz
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Silenciar loggers de terceros molestos
for noisy_logger in ["WDM", "urllib3", "selenium"]:
    logging.getLogger(noisy_logger).setLevel(logging.WARNING)

# Exportar si necesitas usar el nombre del log o timestamp
LOG_FILE = log_file
TIMESTAMP = timestamp