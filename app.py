from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from highlight import save_highlight, remove_highlight, get_highlights
from pyqs import get_pyq_matches
from highlighter import detect_highlights
import traceback
import os
import json

app = Flask(__name__, static_url_path='/static', static_folder='static')
CORS(app, resources={r"/api/": {"origins": "*"}}, supports_credentials=True)

# ✅ Load chapter (images + texts)
@app.route('/api/load_chapter', methods=['POST'])
def load_chapter():
    try:
        data = request.json
        book = data.get('book')
        chapter = data.get('chapter')
        folder_path = os.path.join("static", "books", book, chapter)

        print(f"[LOAD CHAPTER] book={book}, chapter={chapter}, folder={folder_path}")

        if not os.path.exists(folder_path):
            print("[ERROR] Chapter folder not found")
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
                pages.append({"image": image_url, "text": text_content})
        return jsonify({'pages': pages})
    except Exception as e:
        print("[EXCEPTION] load_chapter:", traceback.format_exc())
        return jsonify({'error': str(e)}), 500

# ✅ Chapter text
@app.route('/api/chapter_text/<book>/<chapter>')
def get_chapter_text(book, chapter):
    try:
        path = f"static/text/{book}/{chapter}.txt"
        print(f"[GET CHAPTER TEXT] {path}")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return jsonify({"text": f.read()})
        print("[ERROR] Text file not found")
        return jsonify({"error": "Text file not found"}), 404
    except Exception as e:
        print("[EXCEPTION] get_chapter_text:", traceback.format_exc())
        return jsonify({'error': str(e)}), 500

# ✅ Get highlights
@app.route('/api/chapter_highlights/<book>/<chapter>')
def get_chapter_highlights(book, chapter):
    try:
        print(f"[GET HIGHLIGHTS] book={book}, chapter={chapter}")
        highlights = get_highlights(book, chapter)
        print(f"[HIGHLIGHTS RETURNED] {len(highlights)} found")
        return jsonify({"highlights": highlights})
    except Exception as e:
        print("[EXCEPTION] get_chapter_highlights:", traceback.format_exc())
        return jsonify({'error': str(e)}), 500

# ✅ Save highlight
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

        print(f"\n[HIGHLIGHT REQUEST] book={book}, chapter={chapter}, category={category}")
        print(f"Text len={len(text)}, start={start}, end={end}")

        if not all([book, chapter, text, category]):
            print("[ERROR] Missing fields in highlight request")
            return jsonify({'error': 'Missing book, chapter, text or category'}), 400

        if start is not None and end is not None:
            print("[MANUAL HIGHLIGHT]")
            save_highlight(book, chapter, text, int(start), int(end), category)
        else:
            print("[AUTO HIGHLIGHT]")
            matches = detect_highlights(text, category)
            print(f"Detected {len(matches)} highlights.")
            for match in matches:
                highlight_text = text[match["start"]:match["end"]]
                print(f"Saving highlight: '{highlight_text}' at {match['start']}–{match['end']}")
                save_highlight(book, chapter, highlight_text, match["start"], match["end"], category)

        highlights = get_highlights(book, chapter)
        print(f"[RETURNING HIGHLIGHTS] Total: {len(highlights)}")
        return jsonify({
            'message': 'Highlight(s) saved',
            'highlights': highlights
        })
    except Exception as e:
        print("[EXCEPTION] highlight_line:", traceback.format_exc())
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

        print(f"[REMOVE HIGHLIGHT] book={book}, chapter={chapter}, category={category}")
        print(f"Text: {text}, Range: {start}–{end}")

        if not all([book, chapter, text, start, end, category]):
            print("[ERROR] Missing fields in remove_highlight")
            return jsonify({'error': 'Missing book, chapter, text, start, end or category'}), 400

        remove_highlight(book, chapter, text, int(start), int(end), category)
        print("[HIGHLIGHT REMOVED]")
        return jsonify({'message': 'Highlight removed'})
    except Exception as e:
        print("[EXCEPTION] unhighlight_line:", traceback.format_exc())
        return jsonify({'error': str(e)}), 500

# ✅ PYQ match
@app.route('/api/pyq_match', methods=['POST'])
def pyq_match():
    try:
        data = request.json
        chapter_text = data.get('chapter_text')
        print(f"[PYQ MATCH] Length of chapter_text: {len(chapter_text)}")

        matches = get_pyq_matches(chapter_text)
        print(f"Found {len(matches)} PYQ matches.")

        enhanced = []
        for match in matches:
            enhanced.append({
                'text': match['text'],
                'start': match['start'],
                'end': match['end'],
                'category': 'PYQ',
                'year': match.get('year')
            })

        return jsonify({'matches': enhanced})
    except Exception as e:
        print("[EXCEPTION] pyq_match:", traceback.format_exc())
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

        print(f"[SAVED ALL HIGHLIGHTS] {save_path} written with {len(highlights)} items.")
        return jsonify({"message": "Highlights saved successfully"})
    except Exception as e:
        print("[EXCEPTION] save_all_highlights:", traceback.format_exc())
        return jsonify({'error': str(e)}), 500

# ✅ Serve image
@app.route('/static/books/<book>/<chapter>/<filename>')
def serve_static_image(book, chapter, filename):
    try:
        print(f"[SERVE IMAGE] {book}/{chapter}/{filename}")
        return send_from_directory(f'static/books/{book}/{chapter}', filename)
    except Exception as e:
        print("[EXCEPTION] serve_static_image:", traceback.format_exc())
        return "Error loading image", 500

# ✅ CORS
@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
    return response

# ✅ Start
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    print(f"\n🚀 Server starting at http://0.0.0.0:{port}")
    app.run(host="0.0.0.0", port=port, debug=True)
