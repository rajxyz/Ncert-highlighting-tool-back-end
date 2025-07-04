import os
import json
import traceback
import urllib.parse  # ✅ required to encode URLs properly

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
            if img_file.endswith(('.png', '.jpg', '.jpeg')):
                print(f"🖼️ Adding image file: {img_file}")
                
                # ✅ Encode spaces/special characters in URL
                encoded_url = urllib.parse.quote(f"/static/books/{book}/{chapter}/{img_file}")

                pages.append({
                    'page_number': img_file.split('.')[0],
                    'image': encoded_url
                })

        if not pages:
            print("⚠️ No image pages found in the folder.")
        return pages

    except Exception as e:
        print("❌ Error while reading chapter pages:")
        print(traceback.format_exc())
        raise e
