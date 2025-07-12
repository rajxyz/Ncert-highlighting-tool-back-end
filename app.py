from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from highlight import save_highlight, remove_highlight, get_highlights
from pyqs import get_pyq_matches
import traceback
import os
import json

app = Flask(__name__, static_url_path='/static', static_folder='static')
CORS(app, resources={r"/api/": {"origins": ""}}, supports_credentials=True)

print("✅ Flask app initialized")
print("📦 Static folder:", app.static_folder)

# Load chapter images and text
@app.route('/api/load_chapter', methods=['POST'])
def load_chapter():
    try:
        data = request.json
        book = data.get('book')
        chapter = data.get('chapter')
        print("📘 /api/load_chapter called with:", data)

        if not book or not chapter:
            return jsonify({'error': 'Book and Chapter are required'}), 400

        folder_path = os.path.join("static", "books", book, chapter)
        print(f"📂 Looking for folder: {folder_path}")

        if not os.path.exists(folder_path):
            print("❌ Folder not found.")
            return jsonify({'error': 'Chapter folder not found'}), 404

        files = sorted(os.listdir(folder_path))
        print(f"📁 Found {len(files)} files in folder: {files}")

        pages = []
        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                image_url = f"/static/books/{book}/{chapter}/{file}"
                base_name = os.path.splitext(file)[0]
                text_path = os.path.join(folder_path, f"{base_name}.txt")
                text_content = ""

                if os.path.exists(text_path):
                    try:
                        with open(text_path, "r", encoding="utf-8") as f:
                            text_content = f.read()
                        print(f"📄 Loaded text: {base_name}.txt")
                    except Exception as e:
                        print(f"❌ Failed reading {base_name}.txt: {e}")

                pages.append({
                    "image": image_url,
                    "text": text_content
                })
            else:
                print(f"⚠️ Skipping non-image file: {file}")

        print(f"✅ Pages loaded: {len(pages)}")
        return jsonify({'pages': pages})
    except Exception as e:
        print("❌ Exception in /api/load_chapter:")
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

# Chapter text
@app.route('/api/chapter_text/<book>/<chapter>')
def get_chapter_text(book, chapter):
    try:
        path = f"static/text/{book}/{chapter}.txt"
        print(f"📄 Reading text file: {path}")

        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return jsonify({"text": f.read()})

        print("❌ Text file not found")
        return jsonify({"error": "Text file not found"}), 404
    except Exception as e:
        print("❌ Error in /api/chapter_text:")
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

# Highlights
@app.route('/api/chapter_highlights/<book>/<chapter>')
def get_chapter_highlights(book, chapter):
    try:
        print(f"📌 Fetching highlights for: Book={book}, Chapter={chapter}")
        highlights = get_highlights(book, chapter)
        print(f"📋 Total highlights: {len(highlights)}")
        return jsonify({"highlights": highlights})
    except Exception as e:
        print("❌ Error in /api/chapter_highlights:")
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

# ✅ Save single highlight (updated for exact word-level)
@app.route('/api/highlight', methods=['POST'])
def highlight_line():
    try:
        data = request.json
        print("🖍️ Highlight request:", data)

        book = data.get('book')
        chapter = data.get('chapter')
        full_text = data.get('full_text')
        highlighted_text = data.get('highlighted_text')
        category = data.get('category')

        if not all([book, chapter, full_text, highlighted_text, category]):
            return jsonify({'error': 'Missing book, chapter, full_text, highlighted_text or category'}), 400

        save_highlight(book, chapter, full_text, highlighted_text, category)

        highlights = get_highlights(book, chapter)

        return jsonify({
            'message': 'Highlight saved',
            'highlights': highlights
        })
    except Exception as e:
        print("❌ Error in /api/highlight:")
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

# ✅ Remove a single highlight (word-level)
@app.route('/api/remove_highlight', methods=['POST'])
def unhighlight_line():
    try:
        data = request.json
        print("🧽 Unhighlight request:", data)

        book = data.get('book')
        chapter = data.get('chapter')
        full_text = data.get('full_text')
        highlighted_text = data.get('highlighted_text')
        category = data.get('category')

        if not all([book, chapter, full_text, highlighted_text, category]):
            return jsonify({'error': 'Missing book, chapter, full_text, highlighted_text or category'}), 400

        remove_highlight(book, chapter, full_text, highlighted_text, category)
        return jsonify({'message': 'Highlight removed'})
    except Exception as e:
        print("❌ Error in /api/remove_highlight:")
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

# ✅ PYQ Matching
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

# ✅ Save all highlights (bulk)
@app.route('/api/save_highlights', methods=['POST'])
def save_all_highlights():
    try:
        data = request.json
        book = data.get('book')
        chapter = data.get('chapter')
        highlights = data.get('highlights', [])

        print(f"💾 Saving all highlights for {book} - {chapter}")
        print(f"📋 Highlights count: {len(highlights)}")

        folder_path = os.path.join("static", "highlights", book)
        os.makedirs(folder_path, exist_ok=True)

        save_path = os.path.join(folder_path, f"{chapter}.json")
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(highlights, f, ensure_ascii=False, indent=2)

        print(f"✅ Highlights saved at: {save_path}")
        return jsonify({"message": "Highlights saved successfully"})
    except Exception as e:
        print("❌ Error in /api/save_highlights:")
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

# ✅ Serve images
@app.route('/static/books/<book>/<chapter>/<filename>')
def serve_static_image(book, chapter, filename):
    try:
        print(f"📷 Serving image: {book}/{chapter}/{filename}")
        return send_from_directory(f'static/books/{book}/{chapter}', filename)
    except Exception as e:
        print("❌ Error in serve_static_image:")
        print(traceback.format_exc())
        return "Error loading image", 500

# ✅ CORS headers
@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
    return response

# ✅ Start server
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    print(f"🚀 Starting Flask server on port {port}...")
    app.run(host="0.0.0.0", port=port, debug=True)
