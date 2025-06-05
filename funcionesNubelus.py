"""
Módulo: funcionesNubelus.py

Este módulo contiene funciones específicas para la aplicación Nubelus, utilizando Selenium WebDriver.
Actualmente, proporciona una función para iniciar sesión en la plataforma Nubelus.

Funciones:
    - iniciar_sesion(driver): Abre la web de Nubelus y realiza las acciones necesarias para iniciar sesión.
    
Ejemplo de uso:
    from selenium import webdriver
    import funcionesNubelus
    driver = webdriver.Chrome()
    funcionesNubelus.iniciar_sesion(driver)
"""

import webFunctions
import time
import logging
import tkinter as tk
import pandas as pd
from tkinter import ttk
import sys


# URL de la web de Nubelus
WEB_NUBELUS = "https://portal.nubelus.es"
WEB_NUBELUS_ENTIDAD = "https://portal.nubelus.es/?clave=waster2_gestionEntidadesMedioambientales"
WEB_NUBELUS_ENTIDAD_NUEVO = "https://portal.nubelus.es/?clave=waster2_gestionEntidadesMedioambientales&pAccion=NUEVO"
WEB_NUBELUS_ACUERDOS_NUEVO = "https://portal.nubelus.es/?clave=waster2_gestionAcuerdosRepresentacion&pAccion=NUEVO"
WEB_NUBELUS_USUARIO_NUEVO = "https://portal.nubelus.es/?clave=nubelus_gestionUsuarios&pAccion=NUEVO"
WEB_NUBELUS_CENTROS = "https://portal.nubelus.es/?clave=waster2_gestionEntidadesMedioambientalesCentros"
WEB_NUBELUS_CENTROS_NUEVO = "https://portal.nubelus.es/?clave=waster2_gestionEntidadesMedioambientalesCentros&pAccion=NUEVO"

def iniciar_sesion(driver):
    """
    Inicia sesión en la plataforma Nubelus utilizando el driver de Selenium.
    Reintenta hasta 3 veces en caso de error.
    """
    intentos = 3
    for intento in range(intentos):
        try:
            webFunctions.abrir_web(driver, WEB_NUBELUS)
            webFunctions.escribir_en_elemento_por_id(driver, "pNick_gestor", "ecotitan")
            webFunctions.clickar_boton_por_id(driver, "btContinuar")
            webFunctions.escribir_en_elemento_por_placeholder(driver, "Usuario", "dani")
            webFunctions.escribir_en_elemento_por_placeholder(driver, "Contraseña", "123456")
            webFunctions.clickar_boton_por_id(driver, "btAceptar")
            time.sleep(5)  # Tiempo para aceptar el pop-up de Google
            return
        except Exception as error:
            logging.error(f"Error al iniciar sesión en Nubelus (intento {intento+1}): {error}")
            if intento == intentos - 1:
                continuar = preguntar_por_pantalla()
                if continuar:
                    logging.info("Continuando tras error en inicio de sesión...")
                else:
                    logging.info("Saliendo del proceso de inicio de sesión.")
                    driver.quit()
                    sys.exit()
            time.sleep(1)

def crear_proveedor(driver):
    """
    Hace clic en 'Crear proveedor' y acepta el pop-up correspondiente.
    Reintenta hasta 5 veces en caso de error.
    """
    intentos = 10
    for intento in range(intentos):
        try:
            webFunctions.clickar_boton_por_on_click(driver, "crear_proveedor()")
            oldDriver = driver
            popup = webFunctions.encontrar_pop_up_por_id(driver, "div_crear_proveedor")
            webFunctions.clickar_boton_por_clase(popup, "miBoton_cuadrado.aceptar")
            driver = oldDriver
            return
        except Exception as e:
            logging.error(f"Error al crear proveedor (intento {intento+1}): {e}")
            if intento == intentos - 1:
                raise
            time.sleep(0.5)

def crear_cliente(driver):
    """
    Hace clic en 'Crear cliente' y acepta el pop-up correspondiente.
    Reintenta hasta 5 veces en caso de error.
    """
    intentos = 10
    for intento in range(intentos):
        try:
            webFunctions.clickar_boton_por_texto(driver, "Crear cliente")
            oldDriver = driver
            popup = webFunctions.encontrar_pop_up_por_id(driver, "div_crear_cliente")
            webFunctions.clickar_boton_por_clase(popup, "miBoton_cuadrado.aceptar")
            driver = oldDriver
            return
        except Exception as e:
            logging.error(f"Error al crear cliente (intento {intento+1}): {e}")
            if intento == intentos - 1:
                raise
            time.sleep(0.5)

def entrar_en_centro_medioambiental(driver):
  """
  Accede a la sección 'Centros' dentro del área medioambiental y selecciona un registro.
  """
  webFunctions.seleccionar_elemento_por_id(driver, "fContenido_seleccionado", "Centros")
  time.sleep(1)
  webFunctions.clickar_boton_por_clase(driver, "registro")

def comprobar_integridad(driver):
  """
  Comprueba la integridad de los datos en la plataforma Nubelus.
  
  Esta función hace clic en el botón 'Comprobar integridad' y acepta el pop-up correspondiente.
  """
  webFunctions.seleccionar_elemento_por_id(driver, "fContenido_seleccionado", "Integridad")
  time.sleep(1)
  try:
    mensaje = webFunctions.obtener_texto_elemento_por_xpath(driver, "//*[contains(text(), 'El contrato es E3L válido')]")
    if "El contrato es E3L válido" in mensaje:
      return  # Todo correcto, sigue normalmente
  except Exception:
    pass  # No se encontró el texto
  time.sleep(30)

def preguntar_por_pantalla():
    root = tk.Tk()
    root.withdraw()  # Oculta la ventana principal

    win = tk.Toplevel()
    win.title("Error del programa")
    win.geometry("840x340")  # Doble de grande
    win.resizable(False, False)
    win.configure(bg="#f3f3f3")

    # Icono de pregunta estilo Windows 11 (doble de grande)
    icon_canvas = tk.Canvas(win, width=120, height=120, bg="#f3f3f3", highlightthickness=0)
    icon_canvas.create_oval(20, 20, 100, 100, fill="#0078d4", outline="#0078d4")
    icon_canvas.create_text(60, 64, text="?", font=("Segoe UI", 64, "bold"), fill="white")
    icon_canvas.grid(row=0, column=0, rowspan=2, padx=(60, 20), pady=40)

    # Mensaje (doble de grande)
    label = tk.Label(win, text="¿Desea continuar?", font=("Segoe UI", 28), bg="#f3f3f3")
    label.grid(row=0, column=1, sticky="w", pady=(60, 0), padx=(0, 40))

    continuar = False

    def on_continuar():
        continuar = True
        win.destroy()
        root.destroy()

    def on_cerrar():
        continuar = False
        win.destroy()
        root.destroy()

    # Botones estilo Windows 11 (doble de grande)
    style = ttk.Style()
    style.configure("W11.TButton", font=("Segoe UI", 22), padding=16)

    frame = tk.Frame(win, bg="#f3f3f3")
    frame.grid(row=1, column=1, sticky="e", padx=(0, 40), pady=(20, 40))

    btn_continuar = ttk.Button(frame, text="Continuar", command=on_continuar, style="W11.TButton")
    btn_continuar.pack(side="left", padx=(0, 20))
    btn_cerrar = ttk.Button(frame, text="Cerrar el programa", command=on_cerrar, style="W11.TButton")
    btn_cerrar.pack(side="left")

    win.grab_set()
    win.mainloop()
    return continuar