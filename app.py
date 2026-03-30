import sys
from pathlib import Path

# Add the current folder (codescan) to the module search path
sys.path.append(str(Path(__file__).parent.resolve()))

from flask import Flask, request, jsonify, render_template
import os
import sys

# Ensure imports use the sentinel package in the app root, not sentinel/sentinel.py
# (avoid adding sentinel/ itself to sys.path, which makes `import sentinel` resolve to sentinel/sentinel.py)
# sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'sentinel'))

from sentinel.rules.cpp_rules import CPP_RULES
from sentinel.rules.python_rules import PYTHON_RULES
from sentinel.rules.universal_rules import UNIVERSAL_RULES
from database import (init_db, save_file, save_findings, get_all_files,
                      get_file_by_id, get_results_by_file,
                      get_all_findings, delete_file)

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'c', 'cpp', 'h', 'hpp', 'py'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

EXTENSION_MAP = {
    '.cpp': 'cpp', '.cc': 'cpp', '.cxx': 'cpp',
    '.c': 'cpp', '.h': 'cpp', '.hpp': 'cpp',
    '.py': 'python',
}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def detect_language(filename):
    ext = filename.rsplit('.', 1)[1].lower()
    if ext == 'py':
        return 'Python'
    elif ext in {'c', 'cpp', 'h', 'hpp'}:
        return 'C/C++'
    return 'Unknown'

def get_rules(lang):
    rules = UNIVERSAL_RULES[:]
    if lang == 'cpp':
        rules += CPP_RULES
    elif lang == 'python':
        rules += PYTHON_RULES
    return rules

def analyze(filepath, language, file_id):
    """
    Sentinel scans uploaded file for security vulnerabilities.
    """
    import re

    ext = os.path.splitext(filepath)[1].lower()
    lang = EXTENSION_MAP.get(ext)
    if not lang:
        return []

    rules = get_rules(lang)
    findings = []

    metadata_keys = (
        "'id'", '"id"', "'title'", '"title"',
        "'description'", '"description"', "'cwe'", '"cwe"',
        "'severity'", '"severity"', "'pattern'", '"pattern"',
    )

    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
    except Exception:
        return []

    seen = set()
    for line_num, line in enumerate(lines, start=1):
        stripped = line.strip()

        if stripped.startswith('//') or stripped.startswith('#'):
            continue

        if any(stripped.startswith(k) for k in metadata_keys):
            continue

        if re.match(r"""^\s*['"]\s*\w""", stripped) and stripped.endswith(("',", '",', "'", '"')):
            continue

        for rule in rules:
            if re.search(rule['pattern'], line, re.IGNORECASE):
                key = (rule['id'], line_num)
                if key not in seen:
                    seen.add(key)
                    findings.append({
                        'file_id':     file_id,
                        'title':       rule['title'],
                        'severity':    rule['severity'],
                        'line_number': line_num,
                        'code':        line.strip()[:200],
                        'description': rule['description'],
                        'cwe':         rule.get('cwe', ''),
                        'rule_id':     rule['id'],
                    })

    return findings

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

    findings = analyze(filepath, language, file_id)
    save_findings(findings)

    critical = sum(1 for f in findings if f['severity'] == 'CRITICAL')
    high     = sum(1 for f in findings if f['severity'] == 'HIGH')
    medium   = sum(1 for f in findings if f['severity'] == 'MEDIUM')
    low      = sum(1 for f in findings if f['severity'] == 'LOW')

    return jsonify({
        'message':        'File uploaded and scanned successfully',
        'file_id':        file_id,
        'filename':       filename,
        'language':       language,
        'findings_count': len(findings),
        'critical':       critical,
        'high':           high,
        'medium':         medium,
        'low':            low,
    })

@app.route('/files', methods=['GET'])
def get_files():
    return jsonify(get_all_files())

@app.route('/files/<int:file_id>', methods=['GET'])
def get_file(file_id):
    file = get_file_by_id(file_id)
    if not file:
        return jsonify({'error': 'File not found'}), 404
    return jsonify(file)

@app.route('/results', methods=['GET'])
def get_results():
    return jsonify(get_all_findings())

@app.route('/results/<int:file_id>', methods=['GET'])
def get_file_results(file_id):
    return jsonify(get_results_by_file(file_id))

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