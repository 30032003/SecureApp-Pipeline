import os
import sqlite3
import traceback

from flask import (
    Blueprint,
    current_app,
    g,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

vulnerable_bp = Blueprint("vulnerable", __name__, url_prefix="/vulnerable")

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
VULNERABLE_UPLOAD_FOLDER = os.path.join(BASE_DIR, "app", "uploads", "vulnerable")

# Vulnerable Example - Hardcoded Secret
API_SECRET_KEY = "sk_live_hardcoded_secret_12345"
AWS_ACCESS_KEY = "AKIAEXAMPLEHARDCODEDKEY"
AWS_SECRET_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
DATABASE_PASSWORD = "SuperSecretDBPassword123!"


def get_db():
    return g.db


def init_vulnerable_tables(db):
    db.executescript(
        """
        CREATE TABLE IF NOT EXISTS vulnerable_comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            body TEXT NOT NULL,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS user_secrets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            secret_note TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        );
        """
    )
    if db.execute("SELECT COUNT(*) AS c FROM user_secrets").fetchone()["c"] == 0:
        db.executemany(
            """
            INSERT INTO user_secrets (user_id, title, secret_note)
            VALUES (?, ?, ?)
            """,
            [
                (1, "Admin Recovery Codes", "ADMIN-RC-8842-9910-7731"),
                (1, "Internal API Token", API_SECRET_KEY),
            ],
        )
    db.commit()


@vulnerable_bp.route("/")
def index():
    endpoints = [
        {"name": "SQL Injection", "path": "/vulnerable/sql-search?q=admin"},
        {"name": "Reflected XSS", "path": "/vulnerable/xss-reflected?name=Guest"},
        {"name": "Stored XSS", "path": "/vulnerable/xss-stored"},
        {"name": "IDOR", "path": "/vulnerable/idor/secret/1"},
        {"name": "Weak Session Management", "path": "/vulnerable/weak-session"},
        {"name": "Hardcoded Secret", "path": "/vulnerable/hardcoded-secret"},
        {"name": "Security Misconfiguration", "path": "/vulnerable/misconfig"},
        {"name": "Insecure File Upload", "path": "/vulnerable/insecure-upload"},
    ]
    return render_template("vulnerable/index.html", endpoints=endpoints)


@vulnerable_bp.route("/sql-search")
def sql_search():
    query = request.args.get("q", "")

    # Vulnerable Example - SQL Injection
    sql = f"SELECT id, username, email FROM users WHERE username = '{query}'"
    try:
        rows = get_db().execute(sql).fetchall()
    except sqlite3.Error as exc:
        rows = []
        error = str(exc)
        return render_template(
            "vulnerable/sql_search.html",
            query=query,
            rows=rows,
            error=error,
            executed_sql=sql,
        )

    return render_template(
        "vulnerable/sql_search.html",
        query=query,
        rows=rows,
        error=None,
        executed_sql=sql,
    )


@vulnerable_bp.route("/xss-reflected")
def xss_reflected():
    name = request.args.get("name", "Anonymous")

    # Vulnerable Example - Reflected XSS
    html = f"""
    <!DOCTYPE html>
    <html>
    <head><title>Reflected XSS Demo</title></head>
    <body>
        <h1>Hello, {name}!</h1>
        <p>Your search term was reflected without encoding.</p>
        <a href="{url_for('vulnerable.index')}">Back</a>
    </body>
    </html>
    """
    return html


@vulnerable_bp.route("/xss-stored", methods=["GET", "POST"])
def xss_stored():
    db = get_db()

    if request.method == "POST":
        username = request.form.get("username", "anonymous")
        body = request.form.get("body", "")

        # Vulnerable Example - Stored XSS (unsanitized input persisted)
        db.execute(
            """
            INSERT INTO vulnerable_comments (username, body, created_at)
            VALUES (?, ?, datetime('now'))
            """,
            (username, body),
        )
        db.commit()
        return redirect(url_for("vulnerable.xss_stored"))

    comments = db.execute(
        """
        SELECT username, body, created_at
        FROM vulnerable_comments
        ORDER BY id DESC
        """
    ).fetchall()
    return render_template("vulnerable/xss_stored.html", comments=comments)


@vulnerable_bp.route("/idor/secret/<int:secret_id>")
def idor_secret(secret_id):
    # Vulnerable Example - IDOR (no ownership or authorization check)
    secret = get_db().execute(
        """
        SELECT us.id, us.user_id, us.title, us.secret_note, u.username
        FROM user_secrets us
        JOIN users u ON u.id = us.user_id
        WHERE us.id = ?
        """,
        (secret_id,),
    ).fetchone()
    return render_template("vulnerable/idor.html", secret=secret, secret_id=secret_id)


@vulnerable_bp.route("/weak-session", methods=["GET", "POST"])
def weak_session():
    if request.method == "POST":
        user_id = request.form.get("user_id", "1")
        is_admin = request.form.get("is_admin") == "on"

        # Vulnerable Example - Weak Session Management
        # Accepts client-supplied identity without authentication.
        # No session regeneration; session fixation possible via ?session_id=.
        if request.args.get("session_id"):
            session["_fixed_id"] = request.args.get("session_id")

        session["user_id"] = int(user_id)
        session["username"] = f"user_{user_id}"
        session["is_admin"] = is_admin
        session.permanent = True
        current_app.config["SESSION_COOKIE_HTTPONLY"] = False
        current_app.config["SESSION_COOKIE_SECURE"] = False
        current_app.config["PERMANENT_SESSION_LIFETIME"] = 86400 * 365

        return redirect(url_for("profile"))

    return render_template("vulnerable/weak_session.html", session_data=dict(session))


@vulnerable_bp.route("/hardcoded-secret")
def hardcoded_secret():
    # Vulnerable Example - Hardcoded Secret (exposed via endpoint)
    return jsonify(
        {
            "api_secret_key": API_SECRET_KEY,
            "aws_access_key": AWS_ACCESS_KEY,
            "aws_secret_key": AWS_SECRET_KEY,
            "database_password": DATABASE_PASSWORD,
            "message": "Secrets are hardcoded in app/routes/vulnerable.py",
        }
    )


@vulnerable_bp.route("/misconfig")
def misconfig():
    # Vulnerable Example - Security Misconfiguration
    exposed = {
        "debug_mode": current_app.debug,
        "secret_key": current_app.config.get("SECRET_KEY"),
        "upload_folder": current_app.config.get("UPLOAD_FOLDER"),
        "environment_variables": dict(os.environ),
        "hardcoded_api_key": API_SECRET_KEY,
    }
    return render_template("vulnerable/misconfig.html", exposed=exposed)


@vulnerable_bp.route("/misconfig/error")
def misconfig_error():
    # Vulnerable Example - Security Misconfiguration (verbose error disclosure)
    try:
        raise RuntimeError(
            f"Connection failed: postgres://admin:{DATABASE_PASSWORD}@db.internal:5432/secureapp"
        )
    except RuntimeError:
        return (
            f"<pre>{traceback.format_exc()}</pre>"
            f"<p>Database password hint: {DATABASE_PASSWORD}</p>",
            500,
        )


@vulnerable_bp.route("/insecure-upload", methods=["GET", "POST"])
def insecure_upload():
    os.makedirs(VULNERABLE_UPLOAD_FOLDER, exist_ok=True)
    uploaded_files = os.listdir(VULNERABLE_UPLOAD_FOLDER)

    if request.method == "POST":
        file = request.files.get("file")
        if file and file.filename:
            # Vulnerable Example - Insecure File Upload
            # No extension/MIME validation; preserves original filename and path.
            destination = os.path.join(VULNERABLE_UPLOAD_FOLDER, file.filename)
            file.save(destination)
            return redirect(url_for("vulnerable.insecure_upload"))

    uploaded_files = sorted(os.listdir(VULNERABLE_UPLOAD_FOLDER))
    return render_template(
        "vulnerable/insecure_upload.html", uploaded_files=uploaded_files
    )


@vulnerable_bp.route("/insecure-upload/files/<path:filename>")
def insecure_upload_serve(filename):
    # Vulnerable Example - Insecure File Upload (direct public file serving)
    from flask import send_from_directory

    return send_from_directory(VULNERABLE_UPLOAD_FOLDER, filename)
