import os
import json
import xml.etree.ElementTree as ET

def guardar_regage_json(data, output_dir):
    """
    Guarda el contenido en un archivo regage.json en output_dir.
    Si ya existe, crea regage_1.json, regage_2.json, etc. para no sobrescribir.
    """
    base_name = "regage"
    ext = ".json"
    filename = base_name + ext
    counter = 1
    full_path = os.path.join(output_dir, filename)
    while os.path.exists(full_path):
        filename = f"{base_name}_{counter}{ext}"
        full_path = os.path.join(output_dir, filename)
        counter += 1
    with open(full_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return full_path

def extraer_info_xml(path_xml, regage):
    """
    Extrae información relevante del archivo E3L/XML para construir el objeto JSON solicitado.
    """
    tree = ET.parse(path_xml)
    root = tree.getroot()

    # Representante
    nif_representante = ""
    representante = root.find('.//representativeEntity/nationalId')
    if representante is not None and representante.text:
        nif_representante = representante.text.strip()

    # Nombre del representante (de <reasonName>)
    nombre_representante = ""
    representante_nombre = root.find('.//NTTransferOperatorData/entityName/reason/reasonName')
    if representante_nombre is not None and representante_nombre.text:
        nombre_representante = representante_nombre.text.strip()

    # Productor
    nombre_productor = ""
    productor_name = root.find('.//NTProducerData/entityName/fullName/name')
    productor_surname = root.find('.//NTProducerData/entityName/fullName/surname1')
    if productor_name is not None and productor_name.text:
        nombre_productor = productor_name.text.strip()
        if productor_surname is not None and productor_surname.text:
            nombre_productor += " " + productor_surname.text.strip()
    nif_productor = ""
    productor_nif = root.find('.//NTProducerData/entityId/nationalId')
    if productor_nif is not None and productor_nif.text:
        nif_productor = productor_nif.text.strip()

    # Residuo
    nombre_residuo = ""
    residuo = root.find('.//NTResidueIdentification/residueDescription')
    if residuo is not None and residuo.text:
        nombre_residuo = residuo.text.strip()

    # Construir el diccionario con los datos
    data = {
        "nombre_representante": nombre_representante,
        "nif_representante": nif_representante,
        "nombre_productor": nombre_productor,
        "nif_productor": nif_productor,
        "nombre_residuo": nombre_residuo,
        "regage": regage
    }

    # Guardar el JSON en un archivo regage.json
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "regage.json")
    if os.path.exists(output_path):
        with open(output_path, "r", encoding="utf-8") as f:
            try:
                existing_data = json.load(f)
                if not isinstance(existing_data, list):
                    existing_data = [existing_data]
            except json.JSONDecodeError:
                existing_data = []
    else:
        existing_data = []

    existing_data.append(data)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(existing_data, f, ensure_ascii=False, indent=4)

    return data