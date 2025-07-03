from pdf2image import convert_from_path

def convert_pdf_to_images(pdf_path, output_folder):
    pages = convert_from_path(pdf_path)
    for i, page in enumerate(pages):
        page.save(f"{output_folder}/page_{i+1}.png", 'PNG')
