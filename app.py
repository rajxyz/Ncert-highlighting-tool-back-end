from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from books import get_chapter_pages
from highlight import save_highlight, remove_highlight
from pyqs import get_pyq_matches
import traceback  # For detailed error logs

# ✅ Configure static folder correctly for serving images
app = Flask(__name__, static_url_path='/static', static_folder='static')
CORS(app)  # Enable CORS for frontend communication


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

        print(f"🔍 Trying to load pages from: Book={book}, Chapter={chapter}")
        pages = get_chapter_pages(book, chapter)

        print(f"✅ Pages loaded successfully. Total pages: {len(pages)}")
        return jsonify({'pages': pages})

    except Exception as e:
        print("❌ Error in /api/load_chapter:")
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500


@app.route('/api/highlight', methods=['POST'])
def highlight_line():
    try:
        data = request.json
        print("🖍️ Highlight request:", data)
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
        print("❌ Unhighlight request:", data)
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


# ✅ NEW: Auto-highlighting endpoint
@app.route('/api/auto_highlight', methods=['POST'])
def auto_highlight():
    try:
        data = request.json
        book = data.get('book')
        chapter = data.get('chapter')

        if not book or not chapter:
            return jsonify({'error': 'Book and Chapter required'}), 400

        from highlighter import auto_highlight_chapter  # ✅ Import logic
        highlights = auto_highlight_chapter(book, chapter)

        return jsonify({'message': 'Auto-highlighting done', 'highlights': highlights})

    except Exception as e:
        print("❌ Error in auto_highlight:")
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500


# ✅ Serve images explicitly in deployment (important for platforms like Render)
@app.route('/static/books/<book>/<chapter>/<filename>')
def serve_static_image(book, chapter, filename):
    print(f"📷 Serving image: {book}/{chapter}/{filename}")
    return send_from_directory(f'static/books/{book}/{chapter}', filename)


if __name__ == '__main__':
    print("🚀 Starting Flask app in debug mode...")
    app.run(debug=True)
