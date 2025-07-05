def extract_text_from_chapter(book, chapter, only_images=None):
    folder_path = os.path.join("static", "books", book, chapter)
    print(f"📂 Extracting text from folder: {folder_path}")

    if not os.path.exists(folder_path):
        raise FileNotFoundError(f"❌ Folder not found: {folder_path}")

    text_chunks = []

    # ✅ Use only selected images if provided
    if only_images:
        files = only_images
        print(f"📁 Using {len(files)} selected images for OCR: {files}")
    else:
        files = sorted(os.listdir(folder_path))
        print(f"📁 Found {len(files)} files in folder")

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
