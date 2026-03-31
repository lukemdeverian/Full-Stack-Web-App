# CodeScan: Security Analysis Application

A full-stack web application for static security analysis of C, C++, and Python source code. Upload files through a browser-based dashboard, scan them for known vulnerability patterns, and view interactive reports with severity breakdowns, CWE references, and filterable results.

Powered by [Sentinel](https://github.com/lukemdeverian/sentinel), a custom-built static analysis engine.

---

## Features

- **File upload** — drag and drop or click to upload C, C++, and Python files
- **Automated scanning** — powered by Sentinel's rule engine with 30+ vulnerability patterns
- **CWE mapping** — every finding linked to its Common Weakness Enumeration identifier
- **Interactive dashboard** — severity distribution, findings by language, and top CWE charts
- **Filterable results** — filter by severity, language, or search by filename, title, or CWE
- **Persistent storage** — all uploads and findings stored in SQLite
- **REST API** — JSON endpoints for programmatic access to scan results

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | HTML, CSS, JavaScript, Chart.js |
| Backend | Python, Flask |
| Database | SQLite |
| Analysis Engine | Sentinel (custom static analyzer) |

---

## Project Structure
```
codescan/
├── app.py              # Flask server and API endpoints
├── database.py         # SQLite schema and query functions
├── sentinel/           # Sentinel static analysis engine
│   ├── sentinel.py
│   ├── reporter.py
│   └── rules/
│       ├── cpp_rules.py
│       ├── python_rules.py
│       └── universal_rules.py
├── uploads/            # Uploaded files (gitignored)
└── templates/
    └── index.html      # Dashboard frontend
```

---

## Setup

**Requirements:** Python 3.8+

**Install dependencies:**
```bash
pip install flask
```

**Run the server:**
```bash
python app.py
```

**Open the dashboard:**
```
http://127.0.0.1:5000
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/upload` | Upload a file and run security scan |
| `GET` | `/files` | List all uploaded files with finding counts |
| `GET` | `/files/<id>` | Get metadata for a specific file |
| `GET` | `/results` | Get all findings across all files |
| `GET` | `/results/<id>` | Get all findings for a specific file |
| `DELETE` | `/files/<id>` | Delete a file and its findings |

### Example response — `POST /upload`
```json
{
  "message": "File uploaded and scanned successfully",
  "file_id": 3,
  "filename": "test_vulnerable.py",
  "language": "Python",
  "findings_count": 10,
  "critical": 4,
  "high": 4,
  "medium": 2,
  "low": 0
}
```

---

## Vulnerability Categories

Sentinel detects patterns across four severity levels:

**CRITICAL** — Hardcoded credentials, private key material, `eval()`/`exec()`, `gets()`

**HIGH** — Buffer overflows (`strcpy`, `sprintf`, `strcat`), command injection (`system()`, `os.system()`), SQL injection, pickle deserialization, SSL verification disabled, format string vulnerabilities

**MEDIUM** — Weak hashing (MD5/SHA1), unchecked `malloc()`, `rand()` for security, `yaml.load()` without safe loader, Flask debug mode

**LOW** — Hardcoded IP addresses, TODO/FIXME near security-sensitive code

Every finding includes the file name, line number, affected code, description, and a direct link to its CWE entry on [cwe.mitre.org](https://cwe.mitre.org).

---

## About Sentinel

Sentinel is a standalone static analysis tool built to integrate into secure SDLC pipelines. It was built independently before being integrated into CodeScan as the analysis backend.

[View Sentinel on GitHub](https://github.com/lukemdeverian/sentinel)

---

## Author

Luke Deverian — Computer Science, UC San Diego