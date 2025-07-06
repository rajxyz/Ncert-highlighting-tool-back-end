from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from books import get_chapter_pages
from highlight import save_highlight, remove_highlight
from pyqs import get_pyq_matches
import traceback
import os
import json

# ✅ Initialize Flask
app = Flask(__name__, static_url_path='/static', static_folder='static')
CORS(app)

print("✅ Flask app initialized")
print("📦 Static folder:", app.static_folder)

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

# ✅ Load chapter images metadata
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

# ✅ Serve static chapter image
@app.route('/static/books/<book>/<chapter>/<filename>')
def serve_static_image(book, chapter, filename):
    try:
        print(f"📷 Serving image: {book}/{chapter}/{filename}")
        return send_from_directory(f'static/books/{book}/{chapter}', filename)

    except Exception as e:
        print("❌ Error in serve_static_image:")
        print(traceback.format_exc())
        return "Error loading image", 500

# ✅ Run Flask app
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    print(f"🚀 Starting Flask server on port {port}...")
    app.run(host="0.0.0.0", port=port, debug=True)
