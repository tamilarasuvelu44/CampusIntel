# CampusIntel

## AI-Assisted Campus Incident Intelligence Platform

CampusIntel is a Flask and SQLite application for reporting campus
incidents, classifying them with transparent AI-assisted rules, and helping
authorized administrators review patterns and risk indicators.

## Features

- Anonymous incident reporting with optional evidence uploads
- Student and administrator authentication
- AI category, risk, and confidence analysis
- Historical risk score based on location, category, and recent activity
- Administrator incident review and investigation notes
- Audit logging for administrator sign-in activity
- CSRF protection and parameterized SQLite queries

The risk indicator supports administrator judgment. It does not make
disciplinary, legal, or emergency decisions automatically.

## Setup

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:5000/` in a browser. The database is initialized on
startup and existing databases are migrated with the Phase 9 columns.

For deployment, set a strong `SECRET_KEY` in `.env`, set
`SESSION_COOKIE_SECURE=true` behind HTTPS, and run a production WSGI server:

```text
gunicorn app:app
```

Never commit `.env`, the SQLite database, uploaded evidence, or credentials.

## Admin setup

For local development only, open `/create-admin` once, then remove or disable
that route before deployment. The default development account is documented
by the route response and should be changed immediately.