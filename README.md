# CampusStudy Pr

A final year B.Tech project: a polished CampusStudy Pr app that supports student records, attendance tracking, assignment publishing, and campus notices.

## Features
- Admin login with session authentication
- Student registration and deletion
- Attendance logging and history
- Assignment publishing with due dates
- Notice board management
- Dashboard metrics and recent activity

## Setup
1. Install Python 3.11+.
2. Open the project folder.
3. Create and activate a virtual environment:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

4. Set your OpenAI API key if you want ChatGPT support:

```powershell
$env:OPENAI_API_KEY = "your_api_key_here"
```

5. Run the app:

```powershell
python app.py
```

6. Open `http://127.0.0.1:5000` in your browser.

## Library feature
- Browse the B.Tech book catalog for major branches and semesters.
- Add new books to support every course in your curriculum.

## Notes
- The database file `campus.db` is created automatically on first run.
- The app is open access by default; no login is required.
- To protect the app in a real deployment, set a secure `SECRET_KEY` environment variable.
