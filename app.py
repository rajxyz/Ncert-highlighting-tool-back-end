from flask import Flask, request, jsonify
from flask_cors import CORS  # ✅ IMPORT THIS
from books import get_chapter_pages
from highlight import save_highlight, remove_highlight
from pyqs import get_pyq_matches

app = Flask(__name__)
CORS(app)  # ✅ ENABLE CORS FOR ALL ROUTES

@app.route('/api/load_chapter', methods=['POST'])
def load_chapter():
    data = request.json
    print("📘 /api/load_chapter called with:", data)  # 🔍 Debug log
    book = data['book']
    chapter = data['chapter']
    pages = get_chapter_pages(book, chapter)
    print("📄 Returning pages:", pages)  # 🔍 Debug log
    return jsonify({'pages': pages})

@app.route('/api/highlight', methods=['POST'])
def highlight_line():
    data = request.json
    save_highlight(data['book'], data['chapter'], data['line'])
    return jsonify({'message': 'Highlight saved'})

@app.route('/api/remove_highlight', methods=['POST'])
def unhighlight_line():
    data = request.json
    remove_highlight(data['book'], data['chapter'], data['line'])
    return jsonify({'message': 'Highlight removed'})

@app.route('/api/pyq_match', methods=['POST'])
def pyq_match():
    data = request.json
    matches = get_pyq_matches(data['chapter_text'])
    return jsonify({'matches': matches})

if __name__ == '__main__':
    app.run(debug=True)
