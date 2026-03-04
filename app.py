import sqlite3
import re
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# ---------------------------------------------------------------------------
# Database setup
# ---------------------------------------------------------------------------

def get_db():
    """Create an in-memory SQLite DB and seed it with sample educational data."""
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.executescript("""
        CREATE TABLE students (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT,
            major TEXT,
            gpa REAL,
            year INTEGER,
            enrollment_date TEXT
        );

        CREATE TABLE courses (
            id INTEGER PRIMARY KEY,
            code TEXT NOT NULL,
            title TEXT NOT NULL,
            department TEXT,
            credits INTEGER,
            instructor TEXT,
            max_students INTEGER
        );

        CREATE TABLE enrollments (
            id INTEGER PRIMARY KEY,
            student_id INTEGER REFERENCES students(id),
            course_id INTEGER REFERENCES courses(id),
            semester TEXT,
            status TEXT
        );

        CREATE TABLE grades (
            id INTEGER PRIMARY KEY,
            student_id INTEGER REFERENCES students(id),
            course_id INTEGER REFERENCES courses(id),
            semester TEXT,
            grade TEXT,
            score REAL
        );

        INSERT INTO students VALUES
            (1,  'Alice Johnson', 'alice@university.edu', 'Computer Science', 3.9,  3, '2022-09-01'),
            (2,  'Bob Smith',     'bob@university.edu',   'Mathematics',      3.4,  2, '2023-09-01'),
            (3,  'Carol White',   'carol@university.edu', 'Biology',          3.7,  4, '2021-09-01'),
            (4,  'David Brown',   'david@university.edu', 'Computer Science', 2.8,  1, '2024-09-01'),
            (5,  'Eva Martinez',  'eva@university.edu',   'Physics',          3.95, 3, '2022-09-01'),
            (6,  'Frank Lee',     'frank@university.edu', 'Mathematics',      3.1,  2, '2023-09-01'),
            (7,  'Grace Kim',     'grace@university.edu', 'Computer Science', 3.6,  4, '2021-09-01'),
            (8,  'Henry Clark',   'henry@university.edu', 'Biology',          2.5,  1, '2024-09-01'),
            (9,  'Iris Patel',    'iris@university.edu',  'Physics',          3.8,  3, '2022-09-01'),
            (10, 'James Wilson',  'james@university.edu', 'Mathematics',      3.3,  2, '2023-09-01');

        INSERT INTO courses VALUES
            (1,  'CS101',  'Intro to Programming',   'Computer Science', 3, 'Dr. Adams',   40),
            (2,  'CS301',  'Database Systems',       'Computer Science', 3, 'Dr. Baker',   35),
            (3,  'CS401',  'Machine Learning',       'Computer Science', 4, 'Dr. Chen',    30),
            (4,  'MA101',  'Calculus I',             'Mathematics',      4, 'Dr. Davis',   50),
            (5,  'MA301',  'Linear Algebra',         'Mathematics',      3, 'Dr. Evans',   40),
            (6,  'BIO101', 'Cell Biology',           'Biology',          3, 'Dr. Foster',  45),
            (7,  'BIO301', 'Genetics',               'Biology',          4, 'Dr. Garcia',  35),
            (8,  'PH201',  'Classical Mechanics',    'Physics',          4, 'Dr. Harris',  40),
            (9,  'PH301',  'Quantum Physics',        'Physics',          4, 'Dr. Ibrahim', 25),
            (10, 'GE100',  'Academic Writing',       'General',          2, 'Dr. Jackson', 60);

        INSERT INTO enrollments VALUES
            (1,  1, 1, 'Fall 2024',   'Active'),
            (2,  1, 2, 'Fall 2024',   'Active'),
            (3,  1, 3, 'Spring 2025', 'Active'),
            (4,  2, 4, 'Fall 2024',   'Active'),
            (5,  2, 5, 'Spring 2025', 'Active'),
            (6,  3, 6, 'Fall 2024',   'Active'),
            (7,  3, 7, 'Spring 2025', 'Active'),
            (8,  4, 1, 'Fall 2024',   'Active'),
            (9,  5, 8, 'Fall 2024',   'Active'),
            (10, 5, 9, 'Spring 2025', 'Active'),
            (11, 6, 4, 'Fall 2024',   'Active'),
            (12, 7, 1, 'Fall 2024',   'Active'),
            (13, 7, 3, 'Spring 2025', 'Active'),
            (14, 8, 6, 'Fall 2024',   'Active'),
            (15, 9, 8, 'Fall 2024',   'Active'),
            (16, 10,5, 'Fall 2024',   'Active');

        INSERT INTO grades VALUES
            (1,  1, 1, 'Fall 2024',   'A',  96.5),
            (2,  1, 2, 'Fall 2024',   'A',  94.0),
            (3,  2, 4, 'Fall 2024',   'B+', 87.5),
            (4,  3, 6, 'Fall 2024',   'A-', 91.0),
            (5,  4, 1, 'Fall 2024',   'C+', 76.0),
            (6,  5, 8, 'Fall 2024',   'A',  98.0),
            (7,  6, 4, 'Fall 2024',   'B',  83.0),
            (8,  7, 1, 'Fall 2024',   'A-', 92.0),
            (9,  8, 6, 'Fall 2024',   'D',  63.0),
            (10, 9, 8, 'Fall 2024',   'A',  97.0),
            (11, 10,5, 'Fall 2024',   'B-', 80.0),
            (12, 1, 3, 'Spring 2025', 'A',  95.5),
            (13, 5, 9, 'Spring 2025', 'A+', 99.5),
            (14, 3, 7, 'Spring 2025', 'A-', 90.0),
            (15, 7, 3, 'Spring 2025', 'B+', 88.0);
    """)
    conn.commit()
    return conn


DB = get_db()

# ---------------------------------------------------------------------------
# Natural Language -> SQL parser
# ---------------------------------------------------------------------------

STATIC_PATTERNS = [
    (r"how many students",
     "SELECT COUNT(*) AS total_students FROM students;"),
    (r"how many courses",
     "SELECT COUNT(*) AS total_courses FROM courses;"),
    (r"how many enrollments",
     "SELECT COUNT(*) AS total_enrollments FROM enrollments;"),
    (r"(top|best) students?",
     "SELECT id, name, major, gpa FROM students ORDER BY gpa DESC LIMIT 10;"),
    (r"(struggling|failing|low gpa)",
     "SELECT id, name, major, gpa FROM students WHERE gpa < 3.0 ORDER BY gpa ASC;"),
    (r"(machine learning|ml courses?|ai courses?)",
     "SELECT id, code, title, department, credits, instructor FROM courses WHERE title LIKE '%Machine Learning%';"),
    (r"average gpa",
     "SELECT ROUND(AVG(gpa), 2) AS average_gpa FROM students;"),
    (r"average (score|grade)",
     "SELECT ROUND(AVG(score), 2) AS average_score FROM grades;"),
    (r"(instructors?|professors?|teachers?)",
     "SELECT DISTINCT instructor, department FROM courses ORDER BY department;"),
    (r"credits?",
     "SELECT code, title, credits FROM courses ORDER BY credits DESC;"),
    (r"all grades?|show grades?|list grades?",
     """SELECT s.name AS student, c.code, c.title AS course, g.grade, g.score, g.semester
        FROM grades g
        JOIN students s ON g.student_id = s.id
        JOIN courses c  ON g.course_id  = c.id
        ORDER BY g.score DESC;"""),
    (r"enrollments?",
     """SELECT s.name AS student, c.code, c.title AS course, e.semester, e.status
        FROM enrollments e
        JOIN students s ON e.student_id = s.id
        JOIN courses c  ON e.course_id  = c.id
        ORDER BY s.name;"""),
    (r"(all )?students?",
     "SELECT id, name, email, major, gpa, year FROM students ORDER BY name;"),
    (r"(all )?courses?",
     "SELECT id, code, title, department, credits, instructor FROM courses ORDER BY department, code;"),
]


def nl_to_sql(query):
    q = query.strip().lower()

    # GPA above
    m = re.search(r"students? with gpa (?:above|over|greater than|>) *([\d.]+)", q)
    if m:
        t = float(m.group(1))
        return f"SELECT id, name, major, gpa FROM students WHERE gpa > {t} ORDER BY gpa DESC;"

    # GPA below
    m = re.search(r"students? with gpa (?:below|under|less than|<) *([\d.]+)", q)
    if m:
        t = float(m.group(1))
        return f"SELECT id, name, major, gpa FROM students WHERE gpa < {t} ORDER BY gpa ASC;"

    # grades for <name>
    m = re.search(r"grades? for ([a-z]+)", q)
    if m:
        name = m.group(1).capitalize()
        return (
            f"SELECT s.name, c.code, c.title, g.grade, g.score, g.semester "
            f"FROM grades g "
            f"JOIN students s ON g.student_id = s.id "
            f"JOIN courses c  ON g.course_id  = c.id "
            f"WHERE s.name LIKE '%{name}%' ORDER BY g.score DESC;"
        )

    # <name>'s grades
    m = re.search(r"([a-z]+)'s grades?", q)
    if m:
        name = m.group(1).capitalize()
        return (
            f"SELECT s.name, c.code, c.title, g.grade, g.score, g.semester "
            f"FROM grades g "
            f"JOIN students s ON g.student_id = s.id "
            f"JOIN courses c  ON g.course_id  = c.id "
            f"WHERE s.name LIKE '%{name}%' ORDER BY g.score DESC;"
        )

    # courses in <dept>
    m = re.search(r"courses? in (computer science|mathematics|biology|physics|general)", q)
    if m:
        dept = m.group(1).title()
        return f"SELECT id, code, title, credits, instructor FROM courses WHERE department = '{dept}' ORDER BY code;"

    # static patterns
    for pattern, sql in STATIC_PATTERNS:
        if re.search(pattern, q):
            return sql

    # keyword fallback
    if any(w in q for w in ["student", "students", "pupil"]):
        return "SELECT id, name, email, major, gpa, year FROM students ORDER BY name;"
    if any(w in q for w in ["course", "courses", "class", "classes", "subject"]):
        return "SELECT id, code, title, department, credits, instructor FROM courses ORDER BY department;"
    if any(w in q for w in ["grade", "grades", "score", "scores", "mark"]):
        return ("SELECT s.name AS student, c.code, c.title AS course, g.grade, g.score "
                "FROM grades g "
                "JOIN students s ON g.student_id = s.id "
                "JOIN courses c  ON g.course_id  = c.id "
                "ORDER BY g.score DESC;")
    if any(w in q for w in ["enroll", "enrollment", "registered"]):
        return ("SELECT s.name AS student, c.code, c.title, e.semester, e.status "
                "FROM enrollments e "
                "JOIN students s ON e.student_id = s.id "
                "JOIN courses c  ON e.course_id  = c.id "
                "ORDER BY s.name;")

    return None

# ---------------------------------------------------------------------------
# Embedded HTML template
# ---------------------------------------------------------------------------

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>EduQuery AI</title>
  <style>
    :root {
      --bg: #0f1117; --card: #1a1d27; --border: #2a2d3e;
      --accent: #6c63ff; --accent2: #48c9b0;
      --text: #e2e8f0; --muted: #8892a4;
      --error: #fc8181; --radius: 12px;
      --shadow: 0 4px 24px rgba(0,0,0,0.4);
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { background: var(--bg); color: var(--text);
           font-family: 'Segoe UI', system-ui, sans-serif;
           min-height: 100vh; padding: 2rem 1rem; }
    header { text-align: center; margin-bottom: 2.5rem; }
    .logo { font-size: 2.8rem; font-weight: 800;
            background: linear-gradient(135deg, var(--accent), var(--accent2));
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            background-clip: text; }
    .subtitle { color: var(--muted); margin-top: .5rem; font-size: 1rem; }
    .badge { display: inline-block; margin-top: .75rem; padding: .25rem .75rem;
             background: rgba(108,99,255,.15); border: 1px solid rgba(108,99,255,.4);
             border-radius: 99px; font-size: .75rem; color: var(--accent); }
    .card { background: var(--card); border: 1px solid var(--border);
            border-radius: var(--radius); padding: 1.75rem;
            box-shadow: var(--shadow); max-width: 900px; margin: 0 auto 2rem; }
    .search-row { display: flex; gap: .75rem; }
    .search-row input { flex: 1; background: var(--bg); border: 1px solid var(--border);
      border-radius: 8px; color: var(--text); font-size: 1rem;
      padding: .75rem 1rem; outline: none; transition: border-color .2s; }
    .search-row input::placeholder { color: var(--muted); }
    .search-row input:focus { border-color: var(--accent); }
    .search-row button { background: linear-gradient(135deg, var(--accent), #8b5cf6);
      border: none; border-radius: 8px; color: #fff; cursor: pointer;
      font-size: 1rem; font-weight: 600; padding: .75rem 1.5rem;
      transition: opacity .2s; }
    .search-row button:hover { opacity: .88; }
    .samples { margin-top: 1rem; display: flex; flex-wrap: wrap; gap: .5rem; }
    .samples span { font-size: .72rem; color: var(--muted); align-self: center; }
    .chip { background: rgba(108,99,255,.08); border: 1px solid rgba(108,99,255,.25);
            border-radius: 99px; color: var(--accent); cursor: pointer;
            font-size: .75rem; padding: .3rem .75rem; transition: background .15s; }
    .chip:hover { background: rgba(108,99,255,.2); }
    .sql-box { margin-top: 1.25rem; background: #0d1017;
               border: 1px solid var(--border); border-radius: 8px;
               padding: .9rem 1rem; display: none; }
    .sql-box .label { color: var(--accent2); font-size: .7rem; font-weight: 700;
                      letter-spacing: .08em; margin-bottom: .4rem; }
    .sql-box code { color: #a8d8a8; font-family: monospace; font-size: .85rem;
                    white-space: pre-wrap; word-break: break-word; }
    .status { margin-top: 1rem; padding: .6rem 1rem; border-radius: 8px;
              font-size: .88rem; display: none; }
    .status.error { background: rgba(252,129,129,.1); border: 1px solid rgba(252,129,129,.3);
                    color: var(--error); }
    .status.info  { background: rgba(72,201,176,.08); border: 1px solid rgba(72,201,176,.25);
                    color: var(--accent2); }
    .results-wrap { margin-top: 1.5rem; overflow-x: auto; display: none; }
    .result-meta { font-size: .78rem; color: var(--muted); margin-bottom: .6rem; }
    table { width: 100%; border-collapse: collapse; font-size: .88rem; }
    thead th { background: rgba(108,99,255,.12); border-bottom: 2px solid var(--border);
               color: var(--accent); font-weight: 700; padding: .65rem .9rem;
               text-align: left; white-space: nowrap; }
    tbody tr { border-bottom: 1px solid var(--border); }
    tbody tr:hover { background: rgba(255,255,255,.03); }
    tbody td { padding: .6rem .9rem; }
    .gpa-high { color: #48c9b0; font-weight: 700; }
    .gpa-mid  { color: #f6c90e; font-weight: 700; }
    .gpa-low  { color: #fc8181; font-weight: 700; }
    .history-card { max-width: 900px; margin: 0 auto; }
    .history-card h3 { font-size: .85rem; color: var(--muted); margin-bottom: .75rem;
                       text-transform: uppercase; letter-spacing: .06em; }
    .history-list { list-style: none; display: flex; flex-direction: column; gap: .4rem; }
    .history-list li { background: var(--card); border: 1px solid var(--border);
                       border-radius: 8px; cursor: pointer; font-size: .85rem;
                       padding: .5rem .9rem; transition: border-color .15s; }
    .history-list li:hover { border-color: var(--accent); color: var(--accent); }
    .spinner { border: 3px solid var(--border); border-top-color: var(--accent);
               border-radius: 50%; display: inline-block; height: 18px; width: 18px;
               animation: spin .7s linear infinite; vertical-align: middle;
               margin-right: .4rem; }
    @keyframes spin { to { transform: rotate(360deg); } }
    footer { text-align: center; color: var(--muted); font-size: .75rem; margin-top: 3rem; }
    footer a { color: var(--accent); text-decoration: none; }
  </style>
</head>
<body>

<header>
  <div class="logo">EduQuery AI</div>
  <div class="subtitle">Ask anything about your educational database -- in plain English</div>
  <div class="badge">ACUHIT 2026 &nbsp;&middot;&nbsp; Acibadem University Hackathon</div>
</header>

<div class="card">
  <div class="search-row">
    <input id="queryInput" type="text"
           placeholder='Try: "Show students with GPA above 3.5" or "List all courses"'
           autofocus />
    <button id="askBtn" onclick="runQuery()">Ask</button>
  </div>
  <div class="samples">
    <span>Try:</span>
    <div class="chip" onclick="setQuery('Show all students')">All students</div>
    <div class="chip" onclick="setQuery('Students with GPA above 3.5')">GPA &gt; 3.5</div>
    <div class="chip" onclick="setQuery('Show grades for Alice')">Grades for Alice</div>
    <div class="chip" onclick="setQuery('List courses in Computer Science')">CS courses</div>
    <div class="chip" onclick="setQuery('How many students')">Count students</div>
    <div class="chip" onclick="setQuery('Show top students by GPA')">Top students</div>
    <div class="chip" onclick="setQuery('Show all grades')">All grades</div>
    <div class="chip" onclick="setQuery('Average GPA')">Avg GPA</div>
  </div>

  <div class="sql-box" id="sqlBox">
    <div class="label">GENERATED SQL</div>
    <code id="sqlCode"></code>
  </div>
  <div class="status" id="statusMsg"></div>
  <div class="results-wrap" id="resultsWrap">
    <div class="result-meta" id="resultMeta"></div>
    <table>
      <thead id="tableHead"></thead>
      <tbody id="tableBody"></tbody>
    </table>
  </div>
</div>

<div class="history-card" id="historyCard" style="display:none;">
  <h3>Recent Queries</h3>
  <ul class="history-list" id="historyList"></ul>
</div>

<footer>
  Built for <a href="https://acuhit.devpost.com" target="_blank">ACUHIT 2026</a>
  &nbsp;&middot;&nbsp; EduQuery AI &nbsp;&middot;&nbsp; Databases + ML/AI + Education
</footer>

<script>
  const hist = [];
  document.getElementById('queryInput').addEventListener('keydown', e => {
    if (e.key === 'Enter') runQuery();
  });
  function setQuery(t) {
    document.getElementById('queryInput').value = t;
    runQuery();
  }
  function showStatus(msg, type) {
    const el = document.getElementById('statusMsg');
    el.textContent = msg;
    el.className = 'status ' + type;
    el.style.display = 'block';
  }
  async function runQuery() {
    const input = document.getElementById('queryInput');
    const q = input.value.trim();
    if (!q) return;
    const btn = document.getElementById('askBtn');
    btn.innerHTML = '<span class="spinner"></span>Thinking...';
    btn.disabled = true;
    document.getElementById('statusMsg').style.display = 'none';
    document.getElementById('resultsWrap').style.display = 'none';
    document.getElementById('sqlBox').style.display = 'none';
    try {
      const resp = await fetch('/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: q })
      });
      const data = await resp.json();
      if (data.error) {
        showStatus('Warning: ' + data.error, 'error');
      } else if (!data.rows || data.rows.length === 0) {
        showStatus('No results found.', 'info');
      } else {
        document.getElementById('sqlCode').textContent = data.sql;
        document.getElementById('sqlBox').style.display = 'block';
        const head = document.getElementById('tableHead');
        const body = document.getElementById('tableBody');
        head.innerHTML = '<tr>' + data.columns.map(c =>
          '<th>' + c.replace(/_/g,' ').toUpperCase() + '</th>').join('') + '</tr>';
        body.innerHTML = data.rows.map(row =>
          '<tr>' + data.columns.map(col => {
            const val = row[col];
            if (col === 'gpa' && val !== null) {
              const cls = val >= 3.5 ? 'gpa-high' : val >= 3.0 ? 'gpa-mid' : 'gpa-low';
              return '<td><span class="' + cls + '">' + val + '</span></td>';
            }
            return '<td>' + (val !== null && val !== undefined ? val : '&mdash;') + '</td>';
          }).join('') + '</tr>'
        ).join('');
        document.getElementById('resultMeta').textContent =
          data.rows.length + ' row' + (data.rows.length !== 1 ? 's' : '') + ' returned';
        document.getElementById('resultsWrap').style.display = 'block';
        if (!hist.includes(q)) {
          hist.unshift(q);
          if (hist.length > 6) hist.pop();
          const list = document.getElementById('historyList');
          list.innerHTML = hist.map(h =>
            '<li onclick="setQuery(\'' + h.replace(/'/g, "\\'") + '\')">' + h + '</li>'
          ).join('');
          document.getElementById('historyCard').style.display = 'block';
        }
      }
    } catch(err) {
      showStatus('Network error: ' + err.message, 'error');
    } finally {
      btn.innerHTML = 'Ask';
      btn.disabled = false;
    }
  }
</script>
</body>
</html>"""

# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    return render_template_string(HTML)


@app.route("/query", methods=["POST"])
def query():
    data = request.get_json(force=True)
    nl_query = data.get("query", "").strip()
    if not nl_query:
        return jsonify({"error": "Empty query"}), 400
    sql = nl_to_sql(nl_query)
    if sql is None:
        return jsonify({"error": "Could not understand query. Try asking about students, courses, grades, or enrollments."})
    try:
        cur = DB.cursor()
        cur.execute(sql)
        rows = [dict(r) for r in cur.fetchall()]
        columns = [d[0] for d in cur.description] if cur.description else []
        return jsonify({"sql": sql.strip(), "columns": columns, "rows": rows})
    except Exception as e:
        return jsonify({"error": "Database error: " + str(e)}), 500


@app.route("/health")
def health():
    return jsonify({"status": "ok", "app": "EduQuery AI"})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
