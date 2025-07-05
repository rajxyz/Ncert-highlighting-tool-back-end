import os
from pdf2image import convert_from_path
from ocr_engine import extract_text_from_image

def convert_pdf_to_images(pdf_path, output_folder):
    print(f"📄 Converting PDF to images: {pdf_path}")
    pages = convert_from_path(pdf_path)
    os.makedirs(output_folder, exist_ok=True)
    
    for i, page in enumerate(pages):
        image_path = os.path.join(output_folder, f"page_{i+1}.png")
        print(f"🖼️ Saving page {i+1} as image: {image_path}")
        page.save(image_path, 'PNG')

    print(f"✅ PDF conversion completed. Total pages: {len(pages)}")


def extract_text_from_chapter(book, chapter):
    folder_path = os.path.join("static", "books", book, chapter)
    print(f"📂 Extracting text from folder: {folder_path}")

    if not os.path.exists(folder_path):
        raise FileNotFoundError(f"❌ Folder not found: {folder_path}")

    text_chunks = []
    files = sorted(os.listdir(folder_path))
    print(f"📁 Found {len(files)} files")

    for file in files:
        if file.lower().endswith(('.png', '.jpg', '.jpeg')):
            image_path = os.path.join(folder_path, file)
            print(f"🔍 OCR on image: {image_path}")
            try:
                text = extract_text_from_image(image_path)
                text_chunks.append(text)
            except Exception as e:
                print(f"❌ OCR failed for {file}: {e}")

    full_text = "\n".join(text_chunks)
    print(f"📝 Total text length: {len(full_text)} characters")
    return full_text
