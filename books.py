import os
import traceback
import urllib.parse

def get_chapter_pages(book, chapter):
    folder_path = f"static/books/{book}/{chapter}"
    print(f"\n📂 Looking for folder: {folder_path}")

    if not os.path.exists(folder_path):
        print(f"❌ Folder does not exist: {folder_path}")
        raise FileNotFoundError(f"Folder not found: {folder_path}")

    pages = []
    try:
        all_files = os.listdir(folder_path)
        print(f"📁 Found {len(all_files)} files in folder: {all_files}")

        for img_file in sorted(all_files):
            if img_file.lower().endswith(('.png', '.jpg', '.jpeg')):
                full_path = os.path.join(folder_path, img_file)
                file_exists = os.path.exists(full_path)
                file_readable = os.access(full_path, os.R_OK)

                print(f"\n🔍 Processing: {img_file}")
                print(f"   - Full path: {full_path}")
                print(f"   - Exists: {file_exists}, Readable: {file_readable}")

                if not file_exists:
                    print(f"   ❌ File does not exist: {full_path}")
                    continue
                if not file_readable:
                    print(f"   ❌ File is not readable: {full_path}")
                    continue

                # Encode individual parts to avoid encoding slashes
                safe_book = urllib.parse.quote(book)
                safe_chapter = urllib.parse.quote(chapter)
                safe_img = urllib.parse.quote(img_file)

                encoded_url = f"/static/books/{safe_book}/{safe_chapter}/{safe_img}"

                print(f"   ✅ Encoded URL: {encoded_url}")

                pages.append({
                    'page_number': img_file.split('.')[0],
                    'image': encoded_url
                })
            else:
                print(f"⚠️ Skipping non-image file: {img_file}")

        if not pages:
            print("⚠️ No valid image pages found in the folder.")

        return pages

    except Exception as e:
        print("❌ Error while reading chapter pages:")
        print(traceback.format_exc())
        raise e
