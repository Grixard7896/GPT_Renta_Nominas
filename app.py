import streamlit as st
import pytesseract
from pdf2image import convert_from_path
import cv2
import numpy as np
import re
import os

# Función para extraer texto de una imagen
def extract_text_from_image(image_path):
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    text = pytesseract.image_to_string(gray, lang='spa')
    return text

# Función para extraer texto de un PDF
def extract_text_from_pdf(pdf_path):
    images = convert_from_path(pdf_path)
    full_text = ""
    for img in images:
        temp_path = "temp_image.png"
        img.save(temp_path, "PNG")
        full_text += extract_text_from_image(temp_path) + "\n"
        os.remove(temp_path)
    return full_text

# Función para analizar y extraer datos clave de la nómina
def parse_nomina_data(text):
    data = {}
    
    salario_bruto_match = re.search(r"Salario Bruto:\s*(\d+[,.]?\d*)", text, re.IGNORECASE)
    irpf_match = re.search(r"IRPF:\s*(\d+[,.]?\d*)%", text, re.IGNORECASE)
    cotizaciones_match = re.search(r"Seguridad Social:\s*(\d+[,.]?\d*)", text, re.IGNORECASE)
    
    if salario_bruto_match:
        data['Salario Bruto'] = float(salario_bruto_match.group(1).replace(',', '.'))
    if irpf_match:
        data['IRPF Retenido (%)'] = float(irpf_match.group(1).replace(',', '.'))
    if cotizaciones_match:
        data['Cotización Seguridad Social'] = float(cotizaciones_match.group(1).replace(',', '.'))
    
    return data

# Interfaz con Streamlit
st.title("Cálculo de IRPF desde Nómina")
st.write("Sube tu nómina en formato PDF o imagen y extraeremos los datos automáticamente.")

uploaded_file = st.file_uploader("Subir nómina", type=["pdf", "png", "jpg", "jpeg"])

if uploaded_file is not None:
    file_path = f"temp_{uploaded_file.name}"
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    if uploaded_file.name.endswith(".pdf"):
        extracted_text = extract_text_from_pdf(file_path)
    else:
        extracted_text = extract_text_from_image(file_path)
    
    os.remove(file_path)
    
    nomina_data = parse_nomina_data(extracted_text)
    st.write("### Datos extraídos:")
    st.json(nomina_data)
pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"
