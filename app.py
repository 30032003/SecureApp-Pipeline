import os
import sqlite3
import importlib.util
from datetime import datetime
from functools import wraps
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import time

from flask import (
    Flask,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


def _load_vulnerable_module():
    module_path = os.path.join(BASE_DIR, "app", "routes", "vulnerable.py")
    spec = importlib.util.spec_from_file_location("vulnerable_routes", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_vulnerable = _load_vulnerable_module()
vulnerable_bp = _vulnerable.vulnerable_bp
init_vulnerable_tables = _vulnerable.init_vulnerable_tables

DATABASE = os.path.join(BASE_DIR, "secureapp.db")
UPLOAD_FOLDER = os.path.join(BASE_DIR, "app", "uploads")
ALLOWED_EXTENSIONS = {"txt", "pdf", "png", "jpg", "jpeg", "gif", "csv", "json"}
MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB

app = Flask(__name__, static_folder="app/static")
app.register_blueprint(vulnerable_bp)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-only-change-in-production")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(_exception):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()
    db.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            is_admin INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS uploads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            filename TEXT NOT NULL,
            stored_name TEXT NOT NULL,
            uploaded_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        );
        """
    )
    admin = db.execute(
        "SELECT id FROM users WHERE username = ?", ("admin",)
    ).fetchone()
    if admin is None:
        db.execute(
            """
            INSERT INTO users (username, email, password_hash, is_admin, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                "admin",
                "admin@secureapp.local",
                generate_password_hash("Admin123!"),
                1,
                datetime.utcnow().isoformat(),
            ),
        )
    db.commit()
    init_vulnerable_tables(db)


def login_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if "user_id" not in session:
            flash("Please log in to continue.", "warning")
            return redirect(url_for("login"))
        return view(**kwargs)

    return wrapped_view


def admin_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if "user_id" not in session:
            flash("Please log in to continue.", "warning")
            return redirect(url_for("login"))
        if not session.get("is_admin"):
            flash("Admin access required.", "danger")
            return redirect(url_for("profile"))
        return view(**kwargs)

    return wrapped_view


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def current_user():
    if "user_id" not in session:
        return None
    return get_db().execute(
        "SELECT id, username, email, is_admin, created_at FROM users WHERE id = ?",
        (session["user_id"],),
    ).fetchone()


@app.before_request
def load_logged_in_user():
    g.user = current_user()


@app.route("/")
def index():
    if g.user:
        return redirect(url_for("profile"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if g.user:
        return redirect(url_for("profile"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            flash("Username and password are required.", "danger")
            return render_template("login.html")

        user = get_db().execute(
            "SELECT id, username, password_hash, is_admin FROM users WHERE username = ?",
            (username,),
        ).fetchone()

        if user is None or not check_password_hash(user["password_hash"], password):
            flash("Invalid username or password.", "danger")
            return render_template("login.html")

        session.clear()
        session["user_id"] = user["id"]
        session["username"] = user["username"]
        session["is_admin"] = bool(user["is_admin"])
        flash("Welcome back!", "success")
        return redirect(url_for("profile"))

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if g.user:
        return redirect(url_for("profile"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")

        if not username or not email or not password:
            flash("All fields are required.", "danger")
            return render_template("register.html")

        if password != confirm:
            flash("Passwords do not match.", "danger")
            return render_template("register.html")

        if len(password) < 8:
            flash("Password must be at least 8 characters.", "danger")
            return render_template("register.html")

        db = get_db()
        existing = db.execute(
            "SELECT id FROM users WHERE username = ? OR email = ?",
            (username, email),
        ).fetchone()
        if existing:
            flash("Username or email already registered.", "danger")
            return render_template("register.html")

        db.execute(
            """
            INSERT INTO users (username, email, password_hash, is_admin, created_at)
            VALUES (?, ?, ?, 0, ?)
            """,
            (
                username,
                email,
                generate_password_hash(password),
                datetime.utcnow().isoformat(),
            ),
        )
        db.commit()
        flash("Account created. Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))


@app.route("/profile")
@login_required
def profile():
    uploads = get_db().execute(
        """
        SELECT filename, uploaded_at
        FROM uploads
        WHERE user_id = ?
        ORDER BY uploaded_at DESC
        LIMIT 10
        """,
        (g.user["id"],),
    ).fetchall()
    return render_template("profile.html", user=g.user, uploads=uploads)


@app.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    if request.method == "POST":
        if "file" not in request.files:
            flash("No file selected.", "danger")
            return redirect(url_for("upload"))

        file = request.files["file"]
        if file.filename == "":
            flash("No file selected.", "danger")
            return redirect(url_for("upload"))

        if not allowed_file(file.filename):
            flash("File type not allowed.", "danger")
            return redirect(url_for("upload"))

        original_name = secure_filename(file.filename)
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        stored_name = f"{session['user_id']}_{timestamp}_{original_name}"
        file.save(os.path.join(app.config["UPLOAD_FOLDER"], stored_name))

        get_db().execute(
            """
            INSERT INTO uploads (user_id, filename, stored_name, uploaded_at)
            VALUES (?, ?, ?, ?)
            """,
            (
                session["user_id"],
                original_name,
                stored_name,
                datetime.utcnow().isoformat(),
            ),
        )
        get_db().commit()
        flash("File uploaded successfully.", "success")
        return redirect(url_for("upload"))

    user_uploads = get_db().execute(
        """
        SELECT filename, stored_name, uploaded_at
        FROM uploads
        WHERE user_id = ?
        ORDER BY uploaded_at DESC
        """,
        (session["user_id"],),
    ).fetchall()
    return render_template("upload.html", uploads=user_uploads)


@app.route("/admin")
@admin_required
def admin():
    users = get_db().execute(
        """
        SELECT id, username, email, is_admin, created_at
        FROM users
        ORDER BY created_at DESC
        """
    ).fetchall()
    upload_stats = get_db().execute(
        """
        SELECT u.username, COUNT(up.id) AS upload_count
        FROM users u
        LEFT JOIN uploads up ON u.id = up.user_id
        GROUP BY u.id
        ORDER BY upload_count DESC
        """
    ).fetchall()
    return render_template("admin.html", users=users, upload_stats=upload_stats)


with app.app_context():
    init_db()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=os.environ.get("FLASK_DEBUG") == "1")
