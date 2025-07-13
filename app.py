from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from highlight import save_highlight, remove_highlight, get_highlights
from pyqs import get_pyq_matches
import traceback
import os
import json

app = Flask(__name__, static_url_path='/static', static_folder='static')
CORS(app, resources={r"/api/": {"origins": ""}}, supports_credentials=True)

# ✅ Load chapter images and text
@app.route('/api/load_chapter', methods=['POST'])
def load_chapter():
    try:
        data = request.json
        book = data.get('book')
        chapter = data.get('chapter')
        folder_path = os.path.join("static", "books", book, chapter)

        if not os.path.exists(folder_path):
            return jsonify({'error': 'Chapter folder not found'}), 404

        files = sorted(os.listdir(folder_path))
        pages = []
        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                image_url = f"/static/books/{book}/{chapter}/{file}"
                base_name = os.path.splitext(file)[0]
                text_path = os.path.join(folder_path, f"{base_name}.txt")
                text_content = ""
                if os.path.exists(text_path):
                    with open(text_path, "r", encoding="utf-8") as f:
                        text_content = f.read()

                pages.append({
                    "image": image_url,
                    "text": text_content
                })
        return jsonify({'pages': pages})
    except Exception as e:
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

# ✅ Chapter text
@app.route('/api/chapter_text/<book>/<chapter>')
def get_chapter_text(book, chapter):
    try:
        path = f"static/text/{book}/{chapter}.txt"
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return jsonify({"text": f.read()})
        return jsonify({"error": "Text file not found"}), 404
    except Exception as e:
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

# ✅ Get all highlights
@app.route('/api/chapter_highlights/<book>/<chapter>')
def get_chapter_highlights(book, chapter):
    try:
        highlights = get_highlights(book, chapter)
        return jsonify({"highlights": highlights})
    except Exception as e:
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

# ✅ Save single highlight (word-level)
@app.route('/api/highlight', methods=['POST'])
def highlight_line():
    try:
        data = request.json
        book = data.get('book')
        chapter = data.get('chapter')
        text = data.get('text')
        start = data.get('start')
        end = data.get('end')
        category = data.get('category')

        if not all([book, chapter, text, start, end, category]):
            return jsonify({'error': 'Missing book, chapter, text, start, end or category'}), 400

        save_highlight(book, chapter, text, int(start), int(end), category)
        highlights = get_highlights(book, chapter)

        return jsonify({
            'message': 'Highlight saved',
            'highlights': highlights
        })
    except Exception as e:
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

# ✅ Remove highlight
@app.route('/api/remove_highlight', methods=['POST'])
def unhighlight_line():
    try:
        data = request.json
        book = data.get('book')
        chapter = data.get('chapter')
        text = data.get('text')
        start = data.get('start')
        end = data.get('end')
        category = data.get('category')

        if not all([book, chapter, text, start, end, category]):
            return jsonify({'error': 'Missing book, chapter, text, start, end or category'}), 400

        remove_highlight(book, chapter, text, int(start), int(end), category)
        return jsonify({'message': 'Highlight removed'})
    except Exception as e:
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

# ✅ PYQ Match
@app.route('/api/pyq_match', methods=['POST'])
def pyq_match():
    try:
        data = request.json
        matches = get_pyq_matches(data['chapter_text'])

        enhanced_matches = []
        for match in matches:
            enhanced_matches.append({
                'text': match['text'],
                'start': match['start'],
                'end': match['end'],
                'category': 'PYQ',
                'year': match.get('year')
            })

        return jsonify({'matches': enhanced_matches})
    except Exception as e:
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

# ✅ Save all highlights
@app.route('/api/save_highlights', methods=['POST'])
def save_all_highlights():
    try:
        data = request.json
        book = data.get('book')
        chapter = data.get('chapter')
        highlights = data.get('highlights', [])

        folder_path = os.path.join("static", "highlights", book)
        os.makedirs(folder_path, exist_ok=True)

        save_path = os.path.join(folder_path, f"{chapter}.json")
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(highlights, f, ensure_ascii=False, indent=2)

        return jsonify({"message": "Highlights saved successfully"})
    except Exception as e:
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

# ✅ Serve images
@app.route('/static/books/<book>/<chapter>/<filename>')
def serve_static_image(book, chapter, filename):
    try:
        return send_from_directory(f'static/books/{book}/{chapter}', filename)
    except Exception as e:
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
    app.run(host="0.0.0.0", port=port, debug=True)
