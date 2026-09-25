import sqlite3
from pathlib import Path

DATABASE = Path(__file__).resolve().parent / "campusintel.db"


def get_connection():

    conn = sqlite3.connect(str(DATABASE))

    conn.row_factory = sqlite3.Row

    return conn


def create_database():

    conn = get_connection()

    cursor = conn.cursor()

    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            username TEXT UNIQUE NOT NULL,

            password TEXT NOT NULL,

            role TEXT NOT NULL DEFAULT 'student'

        )
    """)

    user_columns = {
        row["name"]
        for row in cursor.execute("PRAGMA table_info(users)").fetchall()
    }

    for column, definition in (
        ("username", "TEXT"),
        ("password", "TEXT"),
        ("role", "TEXT DEFAULT 'student'")
    ):
        if column not in user_columns:
            cursor.execute(
                f"ALTER TABLE users ADD COLUMN {column} {definition}"
            )

    if "email" in user_columns and "password_hash" in user_columns:
        cursor.execute("""
            UPDATE users
            SET username = COALESCE(NULLIF(username, ''), email),
                password = COALESCE(NULLIF(password, ''), password_hash),
                role = COALESCE(NULLIF(role, ''), 'student')
            WHERE username IS NULL OR username = ''
               OR password IS NULL OR password = ''
        """)

    # Reports table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reports (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            report_id TEXT UNIQUE,

            category TEXT,

            description TEXT,

            location TEXT,

            severity TEXT,

            ai_category TEXT,

            risk_level TEXT,

            status TEXT,

            evidence TEXT,

            investigation_notes TEXT,

            updated_at TIMESTAMP,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        )
    """)

    conn.commit()

    existing_columns = {
        row["name"]
        for row in cursor.execute("PRAGMA table_info(reports)").fetchall()
    }

    for column, definition in (
        ("evidence", "TEXT"),
        ("investigation_notes", "TEXT"),
        ("updated_at", "TIMESTAMP"),
        ("ai_confidence", "REAL"),
        ("ai_keywords", "TEXT"),
        ("ai_summary", "TEXT"),
        ("risk_score", "INTEGER DEFAULT 0"),
        ("risk_status", "TEXT DEFAULT 'Normal'"),
        ("risk_recommendation", "TEXT"),
        ("escalation_level", "TEXT DEFAULT 'Level 0 - Normal'")
    ):
        if column not in existing_columns:
            cursor.execute(
                f"ALTER TABLE reports ADD COLUMN {column} {definition}"
            )

    conn.commit()

    conn.close()


def create_user(username, password, role="student"):

    conn = get_connection()

    cursor = conn.cursor()

    try:

        cursor.execute("""
            INSERT INTO users
            (username, password, role)

            VALUES (?, ?, ?)
        """, (
            username,
            password,
            role
        ))

        conn.commit()

        return True

    except sqlite3.IntegrityError:

        return False

    finally:

        conn.close()


def get_user(username):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM users
        WHERE username = ?
    """, (username,))

    user = cursor.fetchone()

    conn.close()

    return user


def insert_report(data):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO reports
        (
            report_id,
            category,
            description,
            location,
            severity,
            ai_category,
            risk_level,
            status,
            ai_confidence,
            risk_score,
            risk_status,
            risk_recommendation,
            escalation_level,
            evidence
        )

        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (

        data["report_id"],
        data["category"],
        data["description"],
        data["location"],
        data["severity"],
        data["ai_category"],
        data["risk_level"],
        "Submitted",
        data.get("ai_confidence"),
        data.get("risk_score", 0),
        data.get("risk_status", "Normal"),
        data.get("risk_recommendation"),
        data.get("escalation_level", "Level 0 - Normal"),
        data.get("evidence")

    ))

    conn.commit()

    conn.close()


def get_location_incident_count(location):
    conn = get_connection()
    result = conn.execute(
        "SELECT COUNT(*) FROM reports WHERE location = ?",
        (location,)
    ).fetchone()
    conn.close()
    return result[0]


def get_category_incident_count(category):
    conn = get_connection()
    result = conn.execute(
        "SELECT COUNT(*) FROM reports WHERE ai_category = ?",
        (category,)
    ).fetchone()
    conn.close()
    return result[0]


def get_recent_incident_count(days=7):
    conn = get_connection()
    result = conn.execute(
        "SELECT COUNT(*) FROM reports "
        "WHERE created_at >= datetime('now', ?)",
        (f"-{int(days)} days",)
    ).fetchone()
    conn.close()
    return result[0]


def get_reports():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM reports
        ORDER BY id DESC
    """)

    reports = cursor.fetchall()

    conn.close()

    return reports


def get_report(report_id):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM reports
        WHERE report_id = ?
    """, (report_id,))

    report = cursor.fetchone()

    conn.close()

    return report
def get_category_statistics():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            ai_category,
            COUNT(*) AS total
        FROM reports
        GROUP BY ai_category
    """)

    rows = cursor.fetchall()

    conn.close()

    return rows


def get_risk_statistics():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            risk_level,
            COUNT(*) AS total
        FROM reports
        GROUP BY risk_level
    """)

    rows = cursor.fetchall()

    conn.close()

    return rows


def get_location_statistics():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            location,
            COUNT(*) AS total
        FROM reports
        GROUP BY location
        ORDER BY total DESC
    """)

    rows = cursor.fetchall()

    conn.close()

    return rows


def get_status_statistics():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            status,
            COUNT(*) AS total
        FROM reports
        GROUP BY status
    """)

    rows = cursor.fetchall()

    conn.close()

    return rows
def get_report_by_id(report_id):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM reports
        WHERE report_id = ?
    """, (report_id,))

    report = cursor.fetchone()

    conn.close()

    return report


def update_incident(
    report_id,
    status,
    investigation_notes
):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        UPDATE reports

        SET
            status = ?,
            investigation_notes = ?,
            updated_at = CURRENT_TIMESTAMP

        WHERE report_id = ?
    """, (
        status,
        investigation_notes,
        report_id
    ))

    conn.commit()

    conn.close()


def update_evidence(
    report_id,
    evidence
):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        UPDATE reports

        SET
            evidence = ?,
            updated_at = CURRENT_TIMESTAMP

        WHERE report_id = ?
    """, (
        evidence,
        report_id
    ))

    conn.commit()

    conn.close()


def add_audit_log(username, action, description, ip_address):

    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            action TEXT,
            description TEXT,
            ip_address TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.execute("""
        INSERT INTO audit_logs
        (username, action, description, ip_address)
        VALUES (?, ?, ?, ?)
    """, (username, action, description, ip_address))
    conn.commit()
    conn.close()


def get_audit_logs():

    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            action TEXT,
            description TEXT,
            ip_address TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    logs = conn.execute("""
        SELECT * FROM audit_logs
        ORDER BY created_at DESC
        LIMIT 100
    """).fetchall()
    conn.close()
    return logs