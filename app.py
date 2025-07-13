from flask import Flask, request, jsonify, send_from_directory  
from flask_cors import CORS  
from highlight import save_detected_highlight, remove_highlight, get_highlights  
from highlighter import detect_highlights  
from pyqs import get_pyq_matches  
import traceback  
import os  
import json  
  
app = Flask(__name__, static_url_path='/static', static_folder='static')  
CORS(app, resources={r"/api/": {"origins": "*"}}, supports_credentials=True)  
  
# ✅ Load chapter (images + text)  
@app.route('/api/load_chapter', methods=['POST'])  
def load_chapter():  
    try:  
        data = request.json  
        book = data.get('book')  
        chapter = data.get('chapter')  
        folder_path = os.path.join("static", "books", book, chapter)  
  
        print(f"[LOAD CHAPTER] {folder_path}")  
  
        if not os.path.exists(folder_path):  
            return jsonify({'error': 'Chapter folder not found'}), 404  
  
        pages = []  
        for file in sorted(os.listdir(folder_path)):  
            if file.lower().endswith(('.jpg', '.jpeg', '.png')):  
                image_url = f"/static/books/{book}/{chapter}/{file}"  
                text_file = os.path.splitext(file)[0] + ".txt"  
                text_path = os.path.join(folder_path, text_file)  
                text_content = ""  
                if os.path.exists(text_path):  
                    with open(text_path, "r", encoding="utf-8") as f:  
                        text_content = f.read()  
                pages.append({"image": image_url, "text": text_content})  
        return jsonify({'pages': pages})  
    except Exception:  
        print("[EXCEPTION] load_chapter:", traceback.format_exc())  
        return jsonify({'error': 'Internal error'}), 500  
  
# ✅ Get raw chapter text  
@app.route('/api/chapter_text/<book>/<chapter>')  
def get_chapter_text(book, chapter):  
    try:  
        path = f"static/text/{book}/{chapter}.txt"  
        print(f"[GET CHAPTER TEXT] {path}")  
        if os.path.exists(path):  
            with open(path, "r", encoding="utf-8") as f:  
                return jsonify({"text": f.read()})  
        return jsonify({"error": "Text file not found"}), 404  
    except Exception:  
        print("[EXCEPTION] get_chapter_text:", traceback.format_exc())  
        return jsonify({'error': 'Internal error'}), 500  
  
# ✅ Get all highlights for chapter  
@app.route('/api/chapter_highlights/<book>/<chapter>')  
def get_chapter_highlights(book, chapter):  
    try:  
        highlights = get_highlights(book, chapter)  
        print(f"[GET HIGHLIGHTS] Found: {len(highlights)}")  
        return jsonify({"highlights": highlights})  
    except Exception:  
        print("[EXCEPTION] get_chapter_highlights:", traceback.format_exc())  
        return jsonify({'error': 'Internal error'}), 500  
  
# ✅ Auto-highlight via rule (no manual text, only category)  
@app.route('/api/highlight', methods=['POST'])  
def highlight_auto():  
    try:  
        data = request.json  
        book = data.get('book')  
        chapter = data.get('chapter')  
        category = data.get('category')  
  
        if not all([book, chapter, category]):  
            return jsonify({'error': 'Missing book, chapter, or category'}), 400  
  
        # ✅ ✅ ✅ ONLY THIS LINE UPDATED:
        matches = detect_highlights(book, chapter)
        print(f"[AUTO-HIGHLIGHT] {len(matches)} matches for '{category}'")  
  
        for match in matches:  
            highlight_text = match['text']  
            save_detected_highlight(book, chapter, highlight_text, match["start"], match["end"], category)  
  
        highlights = get_highlights(book, chapter)  
        return jsonify({  
            'message': f"{len(matches)} highlight(s) saved",  
            'highlights': highlights  
        })  
  
    except Exception:  
        print("[EXCEPTION] highlight_auto:", traceback.format_exc())  
        return jsonify({'error': 'Internal error'}), 500  
  
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
            return jsonify({'error': 'Missing required fields'}), 400  
  
        remove_highlight(book, chapter, text, int(start), int(end), category)  
        return jsonify({'message': 'Highlight removed'})  
    except Exception:  
        print("[EXCEPTION] unhighlight_line:", traceback.format_exc())  
        return jsonify({'error': 'Internal error'}), 500  
  
# ✅ PYQ detection  
@app.route('/api/pyq_match', methods=['POST'])  
def pyq_match():  
    try:  
        data = request.json  
        chapter_text = data.get('chapter_text', "")  
        matches = get_pyq_matches(chapter_text)  
        print(f"[PYQ MATCH] Found: {len(matches)}")  
  
        return jsonify({'matches': matches})  
    except Exception:  
        print("[EXCEPTION] pyq_match:", traceback.format_exc())  
        return jsonify({'error': 'Internal error'}), 500  
  
# ✅ Save all highlights manually (optional use)  
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
  
        print(f"[SAVE ALL] {save_path} → {len(highlights)} items saved")  
        return jsonify({"message": "Highlights saved successfully"})  
    except Exception:  
        print("[EXCEPTION] save_all_highlights:", traceback.format_exc())  
        return jsonify({'error': 'Internal error'}), 500  
  
# ✅ Serve book image  
@app.route('/static/books/<book>/<chapter>/<filename>')  
def serve_static_image(book, chapter, filename):  
    try:  
        return send_from_directory(f'static/books/{book}/{chapter}', filename)  
    except Exception:  
        print("[EXCEPTION] serve_static_image:", traceback.format_exc())  
        return "Error loading image", 500  
  
# ✅ Add CORS headers  
@app.after_request  
def add_cors_headers(response):  
    response.headers["Access-Control-Allow-Origin"] = "*"  
    response.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization"  
    response.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"  
    return response  
  
# ✅ Start the server  
if __name__ == '__main__':  
    port = int(os.environ.get("PORT", 10000))  
    print(f"\n🚀 Server running at http://0.0.0.0:{port}")  
    app.run(host="0.0.0.0", port=port, debug=True)








