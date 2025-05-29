import logging
import loggerConfig
import uiautomation as auto
import uiautomationHandler

def firmar_en_AutoFirma():
    ventana_chrome = uiautomationHandler.obtener_ventana_chrome()
    resultado_autofirma = uiautomationHandler.esperar_popup_y_ejecutar(
        ventana_chrome,
        "¿Abrir AutoFirma?",
        accion=lambda popup: uiautomationHandler.click_boton(ventana_chrome, "¿Abrir AutoFirma?", "Abrir AutoFirma"),
        timeout=10
    )
