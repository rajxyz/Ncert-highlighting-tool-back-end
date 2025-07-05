from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from books import get_chapter_pages
from highlight import save_highlight, remove_highlight
from pyqs import get_pyq_matches
import traceback
import os
from PIL import Image
import pytesseract
import time

# ✅ Configure Flask App
app = Flask(__name__, static_url_path='/static', static_folder='static')
CORS(app)  # Enable CORS for frontend communication

print("✅ Flask app initialized")
print("📦 Static folder:", app.static_folder)


def downscale_image(image_path, max_width=1000):
    image = Image.open(image_path)
    if image.width > max_width:
        ratio = max_width / image.width
        new_size = (int(image.width * ratio), int(image.height * ratio))
        image = image.resize(new_size, Image.ANTIALIAS)
    return image


@app.route('/api/load_chapter', methods=['POST'])
def load_chapter():
    try:
        data = request.json
        print("📘 /api/load_chapter called with:", data)

        book = data.get('book')
        chapter = data.get('chapter')

        if not book or not chapter:
            print("⚠️ Missing book or chapter in request.")
            return jsonify({'error': 'Book and Chapter are required'}), 400

        print(f"🔍 Loading pages for: Book={book}, Chapter={chapter}")
        pages = get_chapter_pages(book, chapter)

        print(f"✅ Pages loaded: {len(pages)}")
        return jsonify({'pages': pages})

    except Exception as e:
        print("❌ Exception in /api/load_chapter:")
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500


@app.route('/api/highlight', methods=['POST'])
def highlight_line():
    try:
        data = request.json
        print("🖍️ Highlight request received:", data)
        save_highlight(data['book'], data['chapter'], data['line'])
        return jsonify({'message': 'Highlight saved'})
    except Exception as e:
        print("❌ Error in highlight_line:")
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500


@app.route('/api/remove_highlight', methods=['POST'])
def unhighlight_line():
    try:
        data = request.json
        print("🧽 Unhighlight request received:", data)
        remove_highlight(data['book'], data['chapter'], data['line'])
        return jsonify({'message': 'Highlight removed'})
    except Exception as e:
        print("❌ Error in unhighlight_line:")
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500


@app.route('/api/pyq_match', methods=['POST'])
def pyq_match():
    try:
        data = request.json
        print("📘 PYQ Match request received.")
        matches = get_pyq_matches(data['chapter_text'])
        print(f"📌 PYQ Matches found: {len(matches)}")
        return jsonify({'matches': matches})
    except Exception as e:
        print("❌ Error in pyq_match:")
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500


@app.route('/api/auto_highlight', methods=['POST'])
def auto_highlight():
    try:
        data = request.json
        book = data.get('book')
        chapter = data.get('chapter')
        mode = data.get('mode', 'default')

        print("🔁 Auto-highlighting API called")
        print("📚 Book:", book)
        print("📖 Chapter:", chapter)
        print("🎯 Mode:", mode)

        if not book or not chapter:
            print("⚠️ Missing book or chapter")
            return jsonify({'error': 'Book and Chapter required'}), 400

        folder_path = f"static/books/{book}/{chapter}"
        image_files = sorted([f for f in os.listdir(folder_path) if f.endswith((".jpg", ".jpeg", ".png"))])

        highlights = []

        for filename in image_files:
            full_path = os.path.join(folder_path, filename)
            try:
                print(f"🔍 OCR on image: {full_path}")
                image = downscale_image(full_path)
                text = pytesseract.image_to_string(image, lang='eng')

                for line in text.splitlines():
                    if any(keyword in line.lower() for keyword in ["definition", "example", "formula", "rule"]):
                        highlights.append(line.strip())

                time.sleep(0.5)  # Prevent memory overload

            except Exception as img_err:
                print(f"❌ Error processing {filename}: {img_err}")

        if not highlights:
            print("⚠️ No highlights returned.")
        else:
            print(f"✅ Found {len(highlights)} highlights.")
            for i, h in enumerate(highlights[:5]):
                print(f"🔹 {i+1}: {h}")

        return jsonify({'message': 'Auto-highlighting complete', 'highlights': highlights})

    except Exception as e:
        print("❌ Error in auto_highlight:")
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500


@app.route('/static/books/<book>/<chapter>/<filename>')
def serve_static_image(book, chapter, filename):
    try:
        print(f"📷 Serving static image: {book}/{chapter}/{filename}")
        return send_from_directory(f'static/books/{book}/{chapter}', filename)
    except Exception as e:
        print("❌ Error serving image:")
        print(traceback.format_exc())
        return "Error loading image", 500


# ✅ Start the Flask app with dynamic port (for Render)
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))  # Render will set PORT
    print(f"🚀 Starting Flask server on port {port}...")
    app.run(host="0.0.0.0", port=port, debug=True)
