import pypdfium2 as pdfium
from PIL import Image


import os

# Paths

pdf_path = 'input.pdf'

output_dir = 'output_images'


# Load a document
pdf = pdfium.PdfDocument(pdf_path)
pdf.get_version()
# List to store image paths
image_paths = []

# Loop over pages and render
for i in range(len(pdf)):
    page = pdf[i]
    page
    width, height = page.get_size()
    width
    height
    image = page.render(scale=3).to_pil()
    image_path = f"output_{i:03d}.jpg"
    image.save(f"output_{i:03d}.jpg", dpi=(300,300))
    image_paths.append(image_path)

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
                     quality=75,
                     version=17,       # Save as PDF version 1.7
                     )

# Example usage
output_pdf_path = 'output_document.pdf'

output_pdf = pdfium.PdfDocument(output_pdf_path)
output_pdf.get_metadata_dict()

images_to_pdf(image_paths, output_pdf_path)

print(f"Saved all pages into {output_pdf_path}")
