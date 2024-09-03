import streamlit as st
import pypdfium2 as pdfium
from PIL import Image
import os
from datetime import datetime
from outil import send_email

def images_to_pdf(image_paths, output_pdf_path):
    """Combine a list of images into a single PDF."""
    first_image = Image.open(image_paths[0])
    image_list = [Image.open(img_path).convert('RGB') for img_path in image_paths[1:]]
    first_image.save(output_pdf_path, save_all=True, append_images=image_list, resolution=300, quality=75)

def main():
    """Main function to handle the Streamlit app."""
    st.title("Creador e integrador de PDFs para VUCEM")
    st.subheader("Genera tus PDFs en 300dpi, sin batallar para Ventanilla Única de Comercio Exterior")
    
    st.sidebar.title("Recibe actualizaciones de las nuevas herramientas de comercio exterior")
    
    email = st.sidebar.text_input(label="Correo", placeholder="escribe tu correo")
    
    if st.sidebar.button("Recibir actualizaciones"):
        register_email(email)
    
    st.sidebar.write("Envianos un email: operaciones@marchainternacional.com")
    
    uploaded_files = st.file_uploader("Selecciona los pdfs que quieres juntar", type="pdf", accept_multiple_files=True)
    
    if uploaded_files:
        process_files(uploaded_files)

def register_email(email):
    """Handle email registration for updates."""
    if email:
        with open("subscribers.txt", "a") as file:
            file.write(email + "\n")
        
        subject = f"Nuevo registro VUCEMAPP {email}"
        body = f"Se ha registrado: {email} \n"
        success = send_email(subject, body, "your_verified_email@example.com")  # Replace with your email
        
        if success:
            st.sidebar.success(f"¡Correo {email} registrado con éxito!")
        else:
            st.sidebar.error("No se pudo enviar el correo.")
    else:
        st.sidebar.error("Por favor, ingrese una dirección de correo electrónico.")

def process_files(uploaded_files):
    """Process the uploaded PDF files and generate a merged PDF."""
    uploaded_file_names = [file.name for file in uploaded_files]
    ordered_file_names = st.multiselect("Arrange the PDFs in desired order", uploaded_file_names, default=uploaded_file_names)
    
    ordered_files = [file for name in ordered_file_names for file in uploaded_files if file.name == name]
    
    if st.button("Generate PDF"):
        image_paths = convert_pdfs_to_images(ordered_files)
        output_pdf_path = generate_pdf(image_paths)
        
        with open(output_pdf_path, "rb") as f:
            st.download_button("Download Merged PDF", f, file_name=os.path.basename(output_pdf_path))
        
        clean_up(image_paths)

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

def clean_up(image_paths):
    """Clean up the generated image files."""
    for img_path in image_paths:
        try:
            os.remove(img_path)
        except FileNotFoundError:
            st.warning(f"File not found: {img_path}")

if __name__ == '__main__':
    main()