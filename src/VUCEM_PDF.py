#src/app2_v4.py
import streamlit as st
import pypdfium2 as pdfium
from PIL import Image
import os
from datetime import datetime
from dotenv import load_dotenv
import smtplib
import ssl
from outil import send_email
import math
import time
import subprocess


load_dotenv()
SESSION_TIMEOUT = 300  # seconds

## EN ESTA VERSION EL ARCHIVO PDF SE CONVERTIRA EN VARIOS SI PESA MAS DE 10 MB.

def images_to_pdf(image_paths, output_pdf_path):
    """Combine a list of images into a single PDF."""
    first_image = Image.open(image_paths[0])
    image_list = [Image.open(img_path).convert('RGB') for img_path in image_paths[1:]]
    first_image.save(output_pdf_path, save_all=True, append_images=image_list, resolution=300, quality=75)


def main():
    st.logo("ESCUDO_LOGO_MARCHA.png", link="https://www.marchainternacional.com")
    col1, col2 = st.columns([1, 5])
    with col2:
        st.title("Generador de PDFs para VUCEM")
        st.subheader("Genera tus PDFs en 300dpi con peso menor a 10MB, sin batallar para Ventanilla Única de Comercio Exterior")
    with col1:
        st.image("VERTICAL_LOGO_MARCHA.png", use_column_width=True )
    
    st.sidebar.title("Recibe actualizaciones de las nuevas herramientas de comercio exterior")
    email = st.sidebar.text_input(label="Correo", placeholder="escribe tu correo")
    if st.sidebar.button("Recibir actualizaciones"):
        register_email(email)
     
    st.sidebar.subheader("¿Quiéres alguna app que simplifique tus procesos de comercio exterior?")
    st.sidebar.markdown(
    """
    <p style="font-size: 16px;">
        <strong>Sitio web:</strong> <a href="https://www.marchainternacional.com" target="_blank">marchainternacional.com</a><br>
        <strong>Celular:</strong> <a href="https://wa.me/528443500729" target="_blank">+52844-350-0729</a><br>
        <strong>Email:</strong> <a href="mailto:operaciones@marchainternacional.com">operaciones@marchainternacional.com</a>
        <strong>Linkedin:</strong> <a href=" https://www.linkedin.com/company/marchainternacional/">@marchainternacional</a>
       
    </p>
    """,
    unsafe_allow_html=True
    )
    
    uploaded_files = st.file_uploader("Selecciona los pdfs que quieres juntar", 
                                      type="pdf", 
                                      accept_multiple_files=True,
                                      help="Arrastra y suelta archivos aquí o haz clic en 'Browse files' para seleccionar los archivos. Límite de 200MB por archivo."
    )
    
    if uploaded_files:
        process_files(uploaded_files)

def convert_pdfs_to_images(files):
    """Convert each page of the PDFs into images."""
    temp_dir = "output_images"
    os.makedirs(temp_dir, exist_ok=True)
    image_paths = []

    for uploaded_file in files:
        pdf = pdfium.PdfDocument(uploaded_file)
        for i in range(len(pdf)):
            page = pdf[i]
            image = page.render(scale=3).to_pil()
            image_path = os.path.join(temp_dir, f"output_{i:03d}_{os.path.basename(uploaded_file.name)}.jpg")
            image.save(image_path, dpi=(300, 300))
            image_paths.append(image_path)
    return image_paths


def generate_pdf(image_paths):
    """Generate a PDF from a list of image paths."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    merged_pdfs_dir = "merged_pdfs"
    os.makedirs(merged_pdfs_dir, exist_ok=True)
    output_pdf_path = os.path.join(merged_pdfs_dir, f"{timestamp}_vucem_300dpi.pdf")
    images_to_pdf(image_paths, output_pdf_path)
    return output_pdf_path

def register_email(email):
    """Handle email registration for updates."""
    if email:
        with open("subscribers.txt", "a") as file:
                file.write(email + "\n")
        subject = f"Nuevo registro VUCEMAPP  {email} "
        body = f"Se ha registrado: {email} \n"
        try: 
            send_email(subject, body) 
            st.sidebar.success(f"¡Correo {email} registrado con éxito!")
        except:
            st.sidebar.error("Fallo en enviar correo.")
    else:
        st.sidebar.error("Por favor, ingrese una dirección de correo electrónico.")

def clean_up(image_paths):
    """Clean up the generated image files."""
    for img_path in image_paths:
        try:
            os.remove(img_path)
        except FileNotFoundError:
            st.warning(f"File not found: {img_path}")

def check_file_size(file_path):
    """Check if the fimport timeile is greater than 10 MB and display a message in Streamlit."""
    file_size = os.path.getsize(file_path)
    file_size_mb = file_size / (1024 * 1024)  # Convert bytes to MB
    
    if file_size_mb < 10:
        st.success(f"El archivo '{os.path.basename(file_path)}' es menor a 10 MB. Su tamaño es de {file_size_mb:.2f} MB.")
        Qpdfs = 1
    else:
        st.warning(f"El archivo '{os.path.basename(file_path)}' es mayor a 10 MB. Su tamaño es de {file_size_mb:.2f} MB.")
        Qpdfs = (math.ceil(file_size_mb/10))
    
    return Qpdfs

def generate_pdfs(image_paths, Qpdfs):
    """Generate multiple PDFs from a list of image paths based on the number of Qpdfs."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    merged_pdfs_dir = "splitted_pdfs"
    os.makedirs(merged_pdfs_dir, exist_ok=True)
    
    # Calculate the number of images per PDF
    images_per_pdf = math.ceil(len(image_paths) / Qpdfs)
    
    pdf_paths = []
    
    for i in range(Qpdfs):
        part_image_paths = image_paths[i * images_per_pdf: (i + 1) * images_per_pdf]
        output_pdf_path = os.path.join(merged_pdfs_dir, f"{timestamp}_vucem_300dpi_parte_{i + 1}.pdf")
        
        if part_image_paths:
            images_to_pdf(part_image_paths, output_pdf_path)
            pdf_paths.append(output_pdf_path)
    
    return pdf_paths

def create_file_url(file_path):
    """Create a temporary URL for the file."""
    # Assuming the file is in a directory accessible via a web server
    base_url = "http://localhost/files/"  # Adjust this base URL to your server setup
    return f"{base_url}{os.path.basename(file_path)}"


def process_files(uploaded_files):
    check_session_timeout()
    """Process the uploaded PDF files and generate a merged PDF."""
    uploaded_file_names = [file.name for file in uploaded_files]
    ordered_file_names = st.multiselect("Acomoda los PDFs en el orden que los requieras", uploaded_file_names, default=uploaded_file_names)
    ordered_files = [file for name in ordered_file_names for file in uploaded_files if file.name == name]
    
    if st.button("Generar PDF"):
        image_paths = convert_pdfs_to_images(ordered_files)
        output_pdf_path = generate_pdf(image_paths)
        Qpdfs = check_file_size(output_pdf_path)
        pdf_paths = []
        if Qpdfs == 1:
            pdf_paths.append(output_pdf_path)
        else:
            pdf_paths = generate_pdfs(image_paths, Qpdfs)
        
        st.session_state['pdf_paths'] = pdf_paths
        
        clean_up(image_paths)
    
    # Display all the download buttons at once
    if 'pdf_paths' in st.session_state:
        for path in st.session_state['pdf_paths']:
            with open(path, "rb") as file:
                st.download_button(
                    label=f"Descargar {os.path.basename(path)}",
                    data=file,
                    file_name=os.path.basename(path),
                )
    # Update the session timestamp on interaction
    st.session_state['session_timestamp'] = time.time()

      
def check_session_timeout():
    current_time = time.time()
    
    if 'session_timestamp' not in st.session_state:
        # Initialize session timestamp
        st.session_state['session_timestamp'] = current_time
    else:
        # Check if the session has expired
        if current_time - st.session_state['session_timestamp'] > SESSION_TIMEOUT:
            # Clear session state when timeout occurs
            st.session_state.clear()

if __name__ == '__main__':
    main()