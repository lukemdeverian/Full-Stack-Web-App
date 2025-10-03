from flask import Flask, request, jsonify, render_template
import os
from database import init_db, save_file, save_findings, get_all_results, get_results_by_file

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'c', 'cpp', 'h', 'hpp', 'py'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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

    # Save file to uploads folder
    filename = file.filename
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    # Detect language
    ext = filename.rsplit('.', 1)[1].lower()
    if ext == 'py':
        language = 'Python'
    elif ext in {'c', 'cpp', 'h', 'hpp'}:
        language = 'C/C++'
    else:
        language = 'Unknown'

    # Save file metadata to database
    file_id = save_file(filename, language)

    findings = analyze(filepath, language, file_id)

    save_findings(findings)

    return jsonify({
        'message': 'File uploaded and scanned successfully',
        'file_id': file_id,
        'filename': filename,
        'language': language,
        'findings_count': len(findings)
    })

@app.route('/results', methods=['GET'])
def get_results():
    results = get_all_results()
    return jsonify(results)

@app.route('/results/<int:file_id>', methods=['GET'])
def get_file_results(file_id):
    results = get_results_by_file(file_id)
    return jsonify(results)

@app.route('/results/<int:file_id>', methods=['DELETE'])
def delete_results(file_id):
    from database import delete_file
    delete_file(file_id)
    return jsonify({'message': f'Results for file {file_id} deleted.'})

def analyze(filepath, language, file_id):
    """
    Placeholder analyzer — returns empty findings for now.
    Will be replaced with Sentinel integration in Phase 2.
    """
    return []

if __name__ == '__main__':
    init_db()
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(debug=True)