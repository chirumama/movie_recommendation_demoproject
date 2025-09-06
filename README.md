# Movie & Series Recommender

Run this project locally without PC-specific paths.

Prerequisites
- Python 3.8+ installed and on PATH
- The dataset file `netflix_titles.csv` placed either in:
  - `app/netflix_titles.csv` (recommended), or
  - project root `netflix_titles.csv`, or
  - any location and set via environment variable `NETFLIX_CSV`

Install and run
1. Open a terminal and change to the project folder:
   cd path/to/your/Flask

2. (Optional) Create and activate a virtual environment:
   - Windows (PowerShell):
     python -m venv .venv
     .\.venv\Scripts\Activate.ps1
   - Windows (CMD):
     python -m venv .venv
     .\.venv\Scripts\activate

3. Install dependencies:
   pip install -r requirement.txt

4. (Optional) If your CSV is not in `app/` or project root, set the env var:
   - Windows (PowerShell):
     $env:NETFLIX_CSV = "C:\full\path\to\netflix_titles.csv"
   - Windows (CMD):
     set NETFLIX_CSV=C:\full\path\to\netflix_titles.csv

5. Start the Flask app:
   python app\app.py
   - The app runs on host `0.0.0.0` and port `5000` by default.

Open the frontend
- In your browser open:
  http://127.0.0.1:5000/index.html
- Do NOT open the HTML file directly from the filesystem (file://). Use the URL above.

Quick checks
- Health endpoint:
  http://127.0.0.1:5000/health — should return `{"status":"ok"}`.
- Root:
  http://127.0.0.1:5000/ — shows server running message.

Troubleshooting
- "CSV not found": place `netflix_titles.csv` in `app/` or project root, or set `NETFLIX_CSV`.
- "Could not connect to backend": ensure Flask is running and check terminal logs.
- Requirements file: the project uses `requirement.txt` at the repo root — install from it.

If problems persist, paste the terminal log and browser console errors.
