import os
import json
import traceback

def get_chapter_pages(book, chapter):
    folder_path = f"static/books/{book}/{chapter}"
    print(f"📂 Looking for folder: {folder_path}")

    if not os.path.exists(folder_path):
        print(f"❌ Folder does not exist: {folder_path}")
        raise FileNotFoundError(f"Folder not found: {folder_path}")

    pages = []
    try:
        all_files = os.listdir(folder_path)
        print(f"📁 Found {len(all_files)} files in folder.")

        for img_file in sorted(all_files):
            if img_file.endswith('.png') or img_file.endswith('.jpg') or img_file.endswith('.jpeg'):
                print(f"🖼️ Adding image file: {img_file}")
                pages.append({
                    'page_number': img_file.split('.')[0],
                    'image': f"/static/books/{book}/{chapter}/{img_file}"
                })

        if not pages:
            print("⚠️ No image pages found in the folder.")
        return pages

    except Exception as e:
        print("❌ Error while reading chapter pages:")
        print(traceback.format_exc())
        raise e
