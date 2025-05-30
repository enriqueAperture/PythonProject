import os
import sys

if getattr(sys, 'frozen', False):
    # Ejecución como ejecutable (.exe), por ejemplo, creado con PyInstaller
    BASE_DIR = os.path.dirname(sys.executable)
else:
    # Ejecución como script (.py)
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))