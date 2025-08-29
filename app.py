from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from highlight import save_detected_highlight, remove_highlight, get_highlights
from highlighter import detect_highlights
from pyqs import get_pyq_matches
import traceback
import os
import json
from werkzeug.utils import secure_filename

app = Flask(__name__, static_url_path='/static', static_folder='static')
CORS(app, resources={r"/api/": {"origins": "*"}}, supports_credentials=True)

# 🧹 Words to skip during highlight auto-detection
JUNK_WORDS = {"the", "a", "an", "in", "on", "and", "of", "at", "to", "for", "is", "are", "was", "by", "from", "this", "that"}

# ✅ Load chapter (images + text)
@app.route('/api/load_chapter', methods=['POST'])
def load_chapter():
    try:
        data = request.json
        book = data.get('book')
        chapter = data.get('chapter')
        folder_path = os.path.join("static", "books", book, chapter)

        print(f"[LOAD CHAPTER] 📘 Folder path: {folder_path}")

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
                else:
                    print(f"⚠️ Missing text file for: {text_file}")
                pages.append({"image": image_url, "text": text_content})

        return jsonify({'pages': pages}), 200
    except Exception:
        print("[EXCEPTION] load_chapter:", traceback.format_exc())
        return jsonify({'error': 'Internal error'}), 500

# ✅ Get raw chapter text
@app.route('/api/chapter_text/<book>/<chapter>')
def get_chapter_text(book, chapter):
    try:
        path = f"static/text/{book}/{chapter}.txt"
        print(f"[GET CHAPTER TEXT] 📄 Path: {path}")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return jsonify({"text": f.read()}), 200
        return jsonify({"error": "Text file not found"}), 404
    except Exception:
        print("[EXCEPTION] get_chapter_text:", traceback.format_exc())
        return jsonify({'error': 'Internal error'}), 500

# ✅ Get all highlights for chapter (with optional filters)
@app.route('/api/chapter_highlights/<book>/<chapter>')
def get_chapter_highlights(book, chapter):
    try:
        page_number = request.args.get('page_number')
        category = request.args.get('category')

        highlights = get_highlights(book, chapter)
        print(f"[GET HIGHLIGHTS] 🎯 Loaded: {len(highlights)}")

        if page_number is not None:
            highlights = [h for h in highlights if str(h.get('page_number')) == str(page_number)]
            print(f"  ↪️ Filtered by page_number={page_number}: {len(highlights)}")

        if category:
            highlights = [h for h in highlights if h.get('category') == category]
            print(f"  ↪️ Filtered by category='{category}': {len(highlights)}")

        return jsonify({"highlights": highlights}), 200
    except Exception:
        print("[EXCEPTION] get_chapter_highlights:", traceback.format_exc())
        return jsonify({'error': 'Internal error'}), 500

# ✅ Auto-highlight (rule-based) with junk filtering
@app.route('/api/highlight', methods=['POST'])
def highlight_auto():
    try:
        data = request.json
        book = data.get('book')
        chapter = data.get('chapter')
        category = data.get('category')
        page = data.get('page')  # ✅ FIXED indentation

        if not all([book, chapter, category]):
            print("⚠️ Missing fields in highlight request")
            return jsonify({'error': 'Missing book, chapter, or category'}), 400

        matches = detect_highlights(book, chapter, categories=[category], page=page)
        print(f"[AUTO-HIGHLIGHT] 🧠 {len(matches)} matches detected for category '{category}'")

        valid_count = 0
        for match in matches:
            highlight_text = match.get('text', '').strip()
            start = match.get('start')
            end = match.get('end')
            page_number = match.get('page_number', 0)
            match_id = match.get("match_id")
            rule_name = match.get("rule_name")
            source = match.get("source", "rule")

            if not highlight_text or start is None or end is None:
                print(f"⚠️ Skipped invalid match (missing data): {match}")
                continue

            if (
                highlight_text.lower() in JUNK_WORDS or
                len(highlight_text.split()) < 2
            ):
                print(f"⚠️ Skipped junk/short highlight: '{highlight_text}'")
                continue

            print(f"✅ Saving highlight → '{highlight_text}' (Page: {page_number})")
            save_detected_highlight(book, chapter, highlight_text, start, end, category, page_number, match_id, rule_name, source)
            valid_count += 1

        highlights = get_highlights(book, chapter)
        print(f"✅ Total highlights after save: {len(highlights)}")

        return jsonify({
            'message': f"{valid_count} valid highlight(s) saved",
            'highlights': highlights
        }), 200
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
        page_number = data.get('page_number') or 0

        if not all([book, chapter, text, start, end, category]):
            return jsonify({'error': 'Missing required fields'}), 400

        print(f"[REMOVE] ❌ Removing '{text}' from page {page_number}")
        remove_highlight(book, chapter, text, int(start), int(end), category, int(page_number))
        return jsonify({'message': 'Highlight removed'}), 200
    except Exception:
        print("[EXCEPTION] unhighlight_line:", traceback.format_exc())
        return jsonify({'error': 'Internal error'}), 500

# ✅ PYQ matching
@app.route('/api/pyq_match', methods=['POST'])
def pyq_match():
    try:
        data = request.json
        chapter_text = data.get('chapter_text', "")
        matches = get_pyq_matches(chapter_text)
        print(f"[PYQ MATCH] 📌 {len(matches)} PYQs found")
        return jsonify({'matches': matches}), 200
    except Exception:
        print("[EXCEPTION] pyq_match:", traceback.format_exc())
        return jsonify({'error': 'Internal error'}), 500

# ✅ Save all highlights manually
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

        print(f"[SAVE ALL] 💾 Saved {len(highlights)} highlights → {save_path}")
        return jsonify({"message": "Highlights saved successfully"}), 200
    except Exception:
        print("[EXCEPTION] save_all_highlights:", traceback.format_exc())
        return jsonify({'error': 'Internal error'}), 500

# ✅ Serve images with security
@app.route('/static/books/<book>/<chapter>/<filename>')
def serve_static_image(book, chapter, filename):
    try:
        safe_filename = secure_filename(filename)
        return send_from_directory(f'static/books/{book}/{chapter}', safe_filename)
    except Exception:
        print("[EXCEPTION] serve_static_image:", traceback.format_exc())
        return "Error loading image", 500

# ✅ Global CORS headers
@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
    return response

# ✅ Start server
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    print(f"\n🚀 Server running at http://0.0.0.0:{port}")
    app.run(host="0.0.0.0", port=port, debug=True)


















































