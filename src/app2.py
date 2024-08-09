import streamlit as st
import pypdfium2 as pdfium
from PIL import Image
import os
from datetime import datetime


def images_to_pdf(image_paths, output_pdf_path):
    # Open the first image
    first_image = Image.open(image_paths[0])

    # Convert the rest of the images to RGB and store in a list
    image_list = []
    for img_path in image_paths[1:]:
        img = Image.open(img_path).convert('RGB')
        image_list.append(img)

    # Save all images into a single PDF
    first_image.save(output_pdf_path, 
                     save_all=True, 
                     append_images=image_list, 
                     resolution=300,
                     quality=75)


def main():
    st.title("PDF Compression and DPI Checker")
     
    uploaded_files = st.file_uploader("Choose PDF files to merge", type="pdf", accept_multiple_files=True)

    if uploaded_files:
        # Reordering PDFs
        uploaded_file_names = [file.name for file in uploaded_files]
        ordered_file_names = st.multiselect("Arrange the PDFs in desired order", uploaded_file_names, default=uploaded_file_names)
        
        # Order the uploaded files according to the user's selection
        ordered_files = [file for name in ordered_file_names for file in uploaded_files if file.name == name]

        
        if st.button("Generate PDF"):
            image_paths = []
            temp_dir = "output_images"
            os.makedirs(temp_dir, exist_ok=True)
            
            for uploaded_file in ordered_files:
                # Load the PDF document
                pdf = pdfium.PdfDocument(uploaded_file)
                
                # Render pages and save as images
                for i in range(len(pdf)):
                    page = pdf[i]
                    width, height = page.get_size()
                    image = page.render(scale=3).to_pil()
                    image_path = f"output_{i:03d}_{uploaded_file.name}.jpg"
                    image.save(image_path, dpi=(300, 300))
                    image_paths.append(image_path)
            
            # Generate a timestamp for the filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Create the merged_pdfs directory if it doesn't exist
            merged_pdfs_dir = os.path.join(os.getcwd(), "merged_pdfs")
            os.makedirs(merged_pdfs_dir, exist_ok=True)

            # Set the output path inside the merged_pdfs directory
            output_pdf_path = os.path.join(merged_pdfs_dir, f"{timestamp}_vucem_300dpi.pdf")
            
            
            # Combine the images into a single PDF
            images_to_pdf(image_paths, output_pdf_path)
            
            # Display a link to download the output PDF
            with open(output_pdf_path, "rb") as f:
                st.download_button("Download Merged PDF", f, file_name=f"{timestamp}_vucem_300dpi.pdf")

            # Clean up images after saving the PDF
            for img_path in image_paths:
                if os.path.exists(img_path):
                    os.remove(img_path)
                else:
                    st.warning(f"File not found: {img_path}")


if __name__ == "__main__":
    main()
