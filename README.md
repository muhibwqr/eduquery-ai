# EduQuery AI

> **AI-powered natural language query interface for educational databases**

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0-green.svg)](https://flask.palletsprojects.com)
[![SQLite](https://img.shields.io/badge/SQLite-in--memory-orange.svg)](https://sqlite.org)
[![License](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)

## What Is EduQuery AI?

EduQuery AI lets students and educators ask plain-English questions about academic data
and instantly receive structured answers -- no SQL knowledge required. Just type
"Show me all students with a GPA above 3.5" and get a clean results table in seconds.

Built for the **ACUHIT Hackathon 2026** at Acibadem University, EduQuery AI addresses
one of the most persistent pain points in educational institutions: making institutional
data accessible to non-technical stakeholders.

---

## Features

- **Natural Language Queries** -- Ask questions in plain English; the NL parser maps intent to SQL automatically
- **Instant Results Table** -- Query results rendered in a clean HTML table
- **Sample Educational Database** -- Pre-loaded with students, courses, enrollments, and grades data
- **Query Transparency** -- See the generated SQL alongside your results so you can learn and verify
- **Zero External Dependencies** -- Runs fully offline; no API keys required
- **Responsive UI** -- Clean, mobile-friendly dark-mode interface
- **Query History** -- Session-level history of your recent queries

---

## Tech Stack

| Layer      | Technology                          |
|------------|-------------------------------------|
| Backend    | Python 3.10+, Flask 3.0             |
| Database   | SQLite (in-memory)                  |
| NL Parser  | Custom keyword-based intent engine  |
| Frontend   | HTML5, CSS3 (inline), JavaScript    |
| Templating | Jinja2 (embedded in Flask)          |

---

## Installation

### Prerequisites
- Python 3.10 or higher
- pip

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/muhibwqr/eduquery-ai.git
cd eduquery-ai

# 2. Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
python app.py
```

Then open your browser at **http://localhost:5000**

---

## Usage

1. Open the app in your browser
2. Type a natural language question in the search box, e.g.:
   - *"Show all students"*
   - *"List courses in Computer Science"*
   - *"Find students with GPA above 3.5"*
   - *"Show grades for Alice"*
   - *"How many students are enrolled?"*
   - *"Show top students by GPA"*
3. Press **Enter** or click **Ask**
4. View your results in the table below, along with the generated SQL

---

## Screenshots

> _Screenshots placeholder -- add images of the UI here_

![EduQuery AI Home Screen](screenshots/home.png)
![Query Results](screenshots/results.png)

---

## Project Structure

```
eduquery-ai/
├── app.py              # Main Flask application (all logic + embedded HTML)
├── requirements.txt    # Python dependencies
└── README.md           # This file
```

---

## What's Next

- Integrate OpenAI / local LLM for richer NL understanding
- Connect to real university database systems (PostgreSQL, MySQL)
- Add CSV/PDF export for query results
- User authentication for student vs. faculty views
- Voice query input via Web Speech API
- Chart/visualization generation from query results

---

## Team

Built for ACUHIT 2026 by **Muhib Waqar**

---

## License

MIT License -- see [LICENSE](LICENSE) for details.
