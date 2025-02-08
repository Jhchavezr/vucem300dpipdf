#pages/scanEffect.py
import streamlit as st
import cv2
import numpy as np
import tempfile
#import fitz  # PyMuPDF
from pdf2image import convert_from_path
from PIL import Image
from fpdf import FPDF
import os

def apply_scan_effect(image):
    """
    Apply a scan-like effect to the given image, preserving color, reducing RGB noise, increasing background greyness, and distorting margins.
    """
    # Convert to numpy array
    img_array = np.array(image)
    
    # Reduce RGB noise
    noise = np.random.normal(0, 0.8, img_array.shape).astype(np.uint8)  # Reduced noise level
    noisy_img = cv2.add(img_array, noise)
    
    # Increase background greyness
    grey_overlay = np.full_like(noisy_img, 100, dtype=np.uint8)  # Light grey overlay
    blended_img = cv2.addWeighted(noisy_img, 0.5, grey_overlay, 0.5, 0)  # Blend to increase greyness
    
    # Apply slight distortion to the margins
    rows, cols, _ = blended_img.shape
    src_points = np.float32([[0, 0], [cols, 0], [0, rows], [cols, rows]])
    dst_points = np.float32([[10, 10], [cols-5, 0], [0, rows-5], [cols, rows-10]])
    matrix = cv2.getPerspectiveTransform(src_points, dst_points)
    scanned = cv2.warpPerspective(blended_img, matrix, (cols, rows))
    
    return Image.fromarray(scanned)

def convert_pdf_to_images(pdf_path):
    """Convert PDF pages to images."""
    images = convert_from_path(pdf_path)
    return images

def save_images_as_pdf(images, output_path):
    """Save a list of images as a single PDF file."""
    pdf = FPDF()
    for image in images:
        temp_img_path = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False).name
        image.save(temp_img_path, format="JPEG")
        pdf.add_page()
        pdf.image(temp_img_path, x=10, y=10, w=190)
        os.remove(temp_img_path)
    pdf.output(output_path, "F")



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


def main():
    #st.set_page_config(page_title="Efecto Escaneado")

    st.title("Efecto de escaneado de PDF")
    st.write("Upload a PDF file to apply a scanned document effect.")
    
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


    uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])
    
    if uploaded_file is not None:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
            temp_pdf.write(uploaded_file.read())
            temp_pdf_path = temp_pdf.name
        
        st.write("Processing the PDF...")
        images = convert_pdf_to_images(temp_pdf_path)
        processed_images = [apply_scan_effect(img) for img in images]
        
        # Show preview
        st.image(processed_images[0], caption="Scanned Effect Applied (Page 1)", use_container_width=True)
        
        # Save processed images as PDF
        output_pdf_path = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf").name
        save_images_as_pdf(processed_images, output_pdf_path)
        
        # Provide download link
        with open(output_pdf_path, "rb") as f:
            st.download_button(label="Download Processed PDF", data=f, file_name="scanned_effect.pdf", mime="application/pdf")

if __name__ == "__main__":
    main()
