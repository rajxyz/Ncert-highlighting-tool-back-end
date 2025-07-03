import os
import json

def get_chapter_pages(book, chapter):
    folder_path = f"static/books/{book}/{chapter}"
    pages = []
    for img_file in sorted(os.listdir(folder_path)):
        if img_file.endswith('.png'):
            pages.append({
                'page_number': img_file.split('.')[0],
                'image': f"/static/books/{book}/{chapter}/{img_file}"
            })
    return pages
