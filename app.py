from flask import Flask, request, jsonify, render_template
import os
from database import init_db, save_file, get_all_files, get_file_by_id, delete_file

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'c', 'cpp', 'h', 'hpp', 'py'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def detect_language(filename):
    ext = filename.rsplit('.', 1)[1].lower()
    if ext == 'py':
        return 'Python'
    elif ext in {'c', 'cpp', 'h', 'hpp'}:
        return 'C/C++'
    return 'Unknown'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed. Upload C, C++, or Python files only.'}), 400

    filename = file.filename
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    language = detect_language(filename)
    file_id = save_file(filename, language)

    return jsonify({
        'message': 'File uploaded successfully',
        'file_id': file_id,
        'filename': filename,
        'language': language
    })

@app.route('/files', methods=['GET'])
def get_files():
    files = get_all_files()
    return jsonify(files)

@app.route('/files/<int:file_id>', methods=['GET'])
def get_file(file_id):
    file = get_file_by_id(file_id)
    if not file:
        return jsonify({'error': 'File not found'}), 404
    return jsonify(file)

@app.route('/files/<int:file_id>', methods=['DELETE'])
def remove_file(file_id):
    file = get_file_by_id(file_id)
    if not file:
        return jsonify({'error': 'File not found'}), 404
    delete_file(file_id)
    return jsonify({'message': f'File {file_id} deleted successfully'})

if __name__ == '__main__':
    init_db()
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(debug=True)