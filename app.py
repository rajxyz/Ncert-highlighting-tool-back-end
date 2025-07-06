from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from books import get_chapter_pages
from highlight import save_highlight, remove_highlight
from pyqs import get_pyq_matches
import traceback
import os
import json
from PIL import Image
import pytesseract
import time

# ✅ Initialize Flask
app = Flask(__name__, static_url_path='/static', static_folder='static')
CORS(app)
print("✅ Flask app initialized")
print("📦 Static folder:", app.static_folder)

# ✅ Image downscaling (for OCR)
def downscale_image(image_path, max_width=1000):
    image = Image.open(image_path)
    if image.width > max_width:
        ratio = max_width / image.width
        new_size = (int(image.width * ratio), int(image.height * ratio))
        image = image.resize(new_size, Image.ANTIALIAS)
    return image

# ✅ Serve chapter text from pre-saved .txt file
@app.route('/api/chapter_text/<book>/<chapter>')
def get_chapter_text(book, chapter):
    try:
        path = f"static/text/{book}/{chapter}.txt"
        print(f"📄 Reading text file: {path}")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return jsonify({"text": f.read()})
        return jsonify({"error": "Text file not found"}), 404
    except Exception as e:
        print("❌ Error in /api/chapter_text:")
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

# ✅ Serve pre-generated highlights
@app.route('/api/chapter_highlights/<book>/<chapter>')
def get_chapter_highlights(book, chapter):
    try:
        path = f"static/highlights/{book}/{chapter}.json"
        print(f"📌 Reading highlight JSON: {path}")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return jsonify({"highlights": json.load(f)})
        return jsonify({"error": "Highlights not found"}), 404
    except Exception as e:
        print("❌ Error in /api/chapter_highlights:")
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

# ✅ Load chapter images
@app.route('/api/load_chapter', methods=['POST'])
def load_chapter():
    try:
        data = request.json
        book = data.get('book')
        chapter = data.get('chapter')
        print("📘 /api/load_chapter called with:", data)

        if not book or not chapter:
            return jsonify({'error': 'Book and Chapter are required'}), 400

        pages = get_chapter_pages(book, chapter)
        print(f"✅ Pages loaded: {len(pages)}")
        return jsonify({'pages': pages})
    except Exception as e:
        print("❌ Exception in /api/load_chapter:")
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

# ✅ Save highlight
@app.route('/api/highlight', methods=['POST'])
def highlight_line():
    try:
        data = request.json
        print("🖍️ Highlight request:", data)
        save_highlight(data['book'], data['chapter'], data['line'])
        return jsonify({'message': 'Highlight saved'})
    except Exception as e:
        print("❌ Error in /api/highlight:")
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

# ✅ Remove highlight
@app.route('/api/remove_highlight', methods=['POST'])
def unhighlight_line():
    try:
        data = request.json
        print("🧽 Unhighlight request:", data)
        remove_highlight(data['book'], data['chapter'], data['line'])
        return jsonify({'message': 'Highlight removed'})
    except Exception as e:
        print("❌ Error in /api/remove_highlight:")
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

# ✅ PYQ matching
@app.route('/api/pyq_match', methods=['POST'])
def pyq_match():
    try:
        data = request.json
        print("📘 PYQ Match request")
        matches = get_pyq_matches(data['chapter_text'])
        print(f"📌 PYQ Matches: {len(matches)}")
        return jsonify({'matches': matches})
    except Exception as e:
        print("❌ Error in /api/pyq_match:")
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

# ✅ Auto highlight from images (legacy)
@app.route('/api/auto_highlight', methods=['POST'])
def auto_highlight():
    try:
        data = request.json
        book = data.get('book')
        chapter = data.get('chapter')
        mode = data.get('mode', 'default')

        print("🔁 Auto-highlighting called")
        print("📚 Book:", book, "📖 Chapter:", chapter, "🎯 Mode:", mode)

        if not book or not chapter:
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

                time.sleep(0.5)
            except Exception as img_err:
                print(f"❌ Error processing {filename}: {img_err}")

        if not highlights:
            print("⚠️ No highlights found.")
        else:
            print(f"✅ Found {len(highlights)} highlights.")
            for i, h in enumerate(highlights[:5]):
                print(f"🔹 {i+1}: {h}")

        return jsonify({'message': 'Auto-highlighting complete', 'highlights': highlights})

    except Exception as e:
        print("❌ Error in auto_highlight:")
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

# ✅ Serve chapter images
@app.route('/static/books/<book>/<chapter>/<filename>')
def serve_static_image(book, chapter, filename):
    try:
        print(f"📷 Serving image: {book}/{chapter}/{filename}")
        return send_from_directory(f'static/books/{book}/{chapter}', filename)
    except Exception as e:
        print("❌ Error in serve_static_image:")
        print(traceback.format_exc())
        return "Error loading image", 500

# ✅ Run Flask App
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    print(f"🚀 Starting Flask server on port {port}...")
    app.run(host="0.0.0.0", port=port, debug=True)
