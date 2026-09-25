from functools import wraps
def admin_required(function):

    @wraps(function)
    def wrapper(*args, **kwargs):

        if session.get("role") != "admin":

            return redirect(
                url_for("admin_login")
            )

        return function(*args, **kwargs)

    return wrapper
import os
import uuid

from werkzeug.utils import secure_filename
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash
)
from flask_wtf import CSRFProtect
try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv():
        return False

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)
from database import (
    create_database,
    create_user,
    get_user,
    insert_report,
    get_reports,
    get_report,
    get_report_by_id,
    update_incident,
    update_evidence,
    get_category_statistics,
    get_risk_statistics,
    get_location_statistics,
    get_status_statistics,
    add_audit_log,
    get_location_incident_count,
    get_category_incident_count,
    get_recent_incident_count
)

from ai_engine import analyze_incident
from risk_engine import (
    calculate_risk_score,
    get_risk_status,
    get_recommendation,
    get_escalation_level
)


load_dotenv()
app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploads"
app.config["SECRET_KEY"] = os.getenv(
    "SECRET_KEY",
    "campusintel-development-secret"
)

app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024
app.config.update(

    SESSION_COOKIE_HTTPONLY=True,

    SESSION_COOKIE_SAMESITE="Lax",

    SESSION_COOKIE_SECURE=os.getenv(
        "SESSION_COOKIE_SECURE",
        "false"
    ).lower() == "true"

)
ALLOWED_EXTENSIONS = {
    "png",
    "jpg",
    "jpeg",
    "pdf"
}

os.makedirs(
    app.config["UPLOAD_FOLDER"],
    exist_ok=True
)

csrf = CSRFProtect(app)

create_database()


def log_security_event(username, action, description):

    add_audit_log(
        username,
        action,
        description,
        request.remote_addr
    )


# =========================
# HOME
# =========================

@app.route("/")
def home():

    return render_template("index.html")


# =========================
# STUDENT REGISTER
# =========================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"].strip()

        password = request.form["password"]

        if len(username) < 3:

            flash("Username must contain at least 3 characters.")

            return redirect(url_for("register"))

        if len(password) < 6:

            flash("Password must contain at least 6 characters.")

            return redirect(url_for("register"))

        hashed_password = generate_password_hash(password)

        success = create_user(
            username,
            hashed_password,
            "student"
        )

        if not success:

            flash("Username already exists.")

            return redirect(url_for("register"))

        flash("Registration successful. Please login.")

        return redirect(url_for("login"))

    return render_template("register.html")


# =========================
# STUDENT LOGIN
# =========================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"].strip()

        password = request.form["password"]

        user = get_user(username)

        if user and check_password_hash(
            user["password"],
            password
        ):

            session["user_id"] = user["id"]

            session["username"] = user["username"]

            session["role"] = user["role"]

            return redirect(url_for("home"))

        flash("Invalid username or password.")

    return render_template("login.html")


# =========================
# LOGOUT
# =========================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("home"))


# =========================
# REPORT INCIDENT
# =========================

@app.route("/report", methods=["GET", "POST"])
def report():

    if request.method == "POST":

        category = request.form["category"]

        description = request.form["description"]

        location = request.form["location"]

        severity = request.form["severity"]

        # -------------------------
        # AI ANALYSIS
        # -------------------------

        ai_category, risk_level, ai_confidence = (
            analyze_incident(description)
        )

        location_count = get_location_incident_count(location)
        category_count = get_category_incident_count(ai_category)
        recent_count = get_recent_incident_count()
        risk_score = calculate_risk_score(
            risk_level,
            location_count,
            recent_count,
            category_count
        )
        risk_status = get_risk_status(risk_score)
        risk_recommendation = get_recommendation(risk_score)
        escalation_level = get_escalation_level(risk_score)

        # -------------------------
        # REPORT ID
        # -------------------------

        report_id = (
            "CI-" +
            uuid.uuid4().hex[:8].upper()
        )

        # -------------------------
        # EVIDENCE
        # -------------------------

        evidence_file = request.files.get(
            "evidence"
        )

        evidence_name = None

        if (
            evidence_file
            and
            evidence_file.filename
        ):

            if not allowed_file(
                evidence_file.filename
            ):

                flash(
                    "Invalid evidence file type."
                )

                return redirect(
                    url_for("report")
                )

            original_name = secure_filename(
                evidence_file.filename
            )

            unique_name = (
                uuid.uuid4().hex
                + "_"
                + original_name
            )

            evidence_path = os.path.join(
                app.config["UPLOAD_FOLDER"],
                unique_name
            )

            evidence_file.save(
                evidence_path
            )

            evidence_name = unique_name

        # -------------------------
        # SAVE REPORT
        # -------------------------

        data = {

            "report_id": report_id,

            "category": category,

            "description": description,

            "location": location,

            "severity": severity,

            "ai_category": ai_category,

            "risk_level": risk_level,

            "ai_confidence": ai_confidence,

            "risk_score": risk_score,

            "risk_status": risk_status,

            "risk_recommendation": risk_recommendation,

            "escalation_level": escalation_level,

            "evidence": evidence_name

        }

        insert_report(data)

        # Save evidence separately
        if evidence_name:

            update_evidence(
                report_id,
                evidence_name
            )

        return render_template(

            "report.html",

            success=True,

            report_id=report_id,

            ai_category=ai_category,

            risk_level=risk_level,

            ai_confidence=ai_confidence,

            risk_score=risk_score,

            risk_status=risk_status,

            risk_recommendation=risk_recommendation,

            escalation_level=escalation_level

        )

    return render_template(
        "report.html",
        success=False
    )


# =========================
# TRACK REPORT
# =========================

@app.route("/track", methods=["GET", "POST"])
def track():

    report = None

    if request.method == "POST":

        report_id = request.form["report_id"].strip()

        report = get_report(report_id)

        if not report:

            flash("Report not found.")

    return render_template(
        "track.html",
        report=report
    )


# =========================
# ADMIN LOGIN
# =========================
@app.route(
    "/admin/login",
    methods=["GET", "POST"]
)
def admin_login():

    if request.method == "POST":

        username = request.form[
            "username"
        ].strip()

        password = request.form[
            "password"
        ]

        user = get_user(username)

        if (
            user
            and user["role"] == "admin"
            and check_password_hash(
                user["password"],
                password
            )
        ):

            session.clear()

            session["user_id"] = user["id"]

            session["username"] = (
                user["username"]
            )

            session["role"] = "admin"

            log_security_event(
                username,
                "ADMIN_LOGIN_SUCCESS",
                "Admin login successful"
            )

            return redirect(
                url_for("dashboard")
            )

        log_security_event(
            username,
            "ADMIN_LOGIN_FAILED",
            "Invalid admin credentials"
        )

        return render_template(
            "admin_login.html",
            error="Invalid admin credentials."
        )

    return render_template(
        "admin_login.html"
    )



# =========================
# ADMIN DASHBOARD
# =========================

@app.route("/admin/dashboard")
def dashboard():

    if session.get("role") != "admin":

        return redirect(
            url_for("admin_login")
        )

    reports = get_reports()

    category_stats = get_category_statistics()

    risk_stats = get_risk_statistics()

    location_stats = get_location_statistics()

    status_stats = get_status_statistics()

    chart_data = {
        "categories": [
            {"label": row["ai_category"], "total": row["total"]}
            for row in category_stats
        ],
        "risks": [
            {"label": row["risk_level"], "total": row["total"]}
            for row in risk_stats
        ],
        "locations": [
            {"label": row["location"], "total": row["total"]}
            for row in location_stats
        ],
        "statuses": [
            {"label": row["status"], "total": row["total"]}
            for row in status_stats
        ]
    }

    return render_template(

        "dashboard.html",

        reports=reports,

        category_stats=category_stats,

        risk_stats=risk_stats,

        location_stats=location_stats,

        status_stats=status_stats,

        chart_data=chart_data

    )


# =========================
# ADMIN LOGOUT
# =========================

@app.route("/admin/logout")
def admin_logout():

    username = session.get(
        "username",
        "unknown"
    )

    log_security_event(
        username,
        "ADMIN_LOGOUT",
        "Admin logged out"
    )

    session.clear()

    return redirect(
        url_for("admin_login")
    )

# =========================
# FILE VALIDATION
# =========================

def allowed_file(filename):

    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in ALLOWED_EXTENSIONS
    )


# =========================
# CREATE ADMIN
# =========================

@app.route("/create-admin")
def create_admin():

    username = "admin"

    password = "Admin@123"

    hashed_password = generate_password_hash(
        password
    )

    success = create_user(
        username,
        hashed_password,
        "admin"
    )

    if success:

        return """
        <h2>Admin created successfully.</h2>
        <p>Username: admin</p>
        <p>Password: Admin@123</p>
        <p>Delete or disable this route before deployment.</p>
        """

    return """
    <h2>Admin already exists.</h2>
    """


@app.route("/admin/incident/<report_id>")
def incident_details(report_id):

    if session.get("role") != "admin":

        return redirect(
            url_for("admin_login")
        )

    report = get_report_by_id(
        report_id
    )

    if not report:

        return "Incident not found", 404

    return render_template(
        "incident.html",
        report=report
    )


@app.route("/admin/risk/<report_id>")
def risk_analysis(report_id):

    if session.get("role") != "admin":

        return redirect(url_for("admin_login"))

    report = get_report_by_id(report_id)

    if not report:

        return "Report not found", 404

    return render_template(
        "risk_analysis.html",
        report=report
    )
@app.route(
    "/admin/incident/<report_id>/update",
    methods=["POST"]
)
def update_incident_route(report_id):

    if session.get("role") != "admin":

        return redirect(
            url_for("admin_login")
        )

    status = request.form["status"]

    notes = request.form[
        "investigation_notes"
    ]

    update_incident(
        report_id,
        status,
        notes
    )

    return redirect(
        url_for(
            "incident_details",
            report_id=report_id
        )
    )
from flask import send_from_directory
@app.route(
    "/admin/evidence/<filename>"
)
def admin_evidence(filename):

    if session.get("role") != "admin":

        return "Unauthorized", 403

    return send_from_directory(
        app.config["UPLOAD_FOLDER"],
        filename
    )


if __name__ == "__main__":

    app.run(debug=True)
