# Intentionally Vulnerable Code — SecureApp-Pipeline

> **Warning:** This application contains deliberately insecure code for DevSecOps training and security scanner validation. Never deploy these patterns to production.

All vulnerable endpoints are prefixed with `/vulnerable/` and documented in `app/routes/vulnerable.py`.

| # | Vulnerability | Route |
|---|---------------|-------|
| 1 | SQL Injection | `/vulnerable/sql-search` |
| 2 | Reflected XSS | `/vulnerable/xss-reflected` |
| 3 | Stored XSS | `/vulnerable/xss-stored` |
| 4 | IDOR | `/vulnerable/idor/secret/<id>` |
| 5 | Weak Session Management | `/vulnerable/weak-session` |
| 6 | Hardcoded Secret | `/vulnerable/hardcoded-secret` |
| 7 | Security Misconfiguration | `/vulnerable/misconfig` |
| 8 | Insecure File Upload | `/vulnerable/insecure-upload` |

---

## 1. SQL Injection

### Vulnerability Name
SQL Injection (CWE-89)

### Vulnerable Code

```python
# Vulnerable Example - SQL Injection
sql = f"SELECT id, username, email FROM users WHERE username = '{query}'"
rows = get_db().execute(sql).fetchall()
```

**Location:** `app/routes/vulnerable.py` — `sql_search()`

User input is concatenated directly into a SQL string instead of using parameterized queries.

### Attack Example

```
GET /vulnerable/sql-search?q=' OR '1'='1
```

This payload closes the string literal and adds an always-true condition, returning all users.

Union-based extraction:

```
GET /vulnerable/sql-search?q=' UNION SELECT id, password_hash, email FROM users --
```

### Risk

- **Confidentiality:** Attackers can read arbitrary database rows (credentials, PII).
- **Integrity:** In writable contexts, attackers can modify or delete data.
- **Availability:** Destructive payloads can destroy data.
- **Compliance:** Data breach exposure; fails PCI-DSS, GDPR, and SOC 2 controls.

---

## 2. Reflected Cross-Site Scripting (XSS)

### Vulnerability Name
Reflected XSS (CWE-79)

### Vulnerable Code

```python
# Vulnerable Example - Reflected XSS
html = f"<h1>Hello, {name}!</h1>"
return html
```

**Location:** `app/routes/vulnerable.py` — `xss_reflected()`

The `name` query parameter is embedded in HTML without encoding or sanitization.

### Attack Example

```
GET /vulnerable/xss-reflected?name=<script>alert(document.cookie)</script>
```

When a victim opens a crafted link, the browser executes attacker-supplied JavaScript in the application origin.

### Risk

- **Session hijacking:** Steal session cookies via `document.cookie`.
- **Phishing:** Inject fake login forms on a trusted domain.
- **Malware delivery:** Redirect users or load external scripts.
- **Scanner detection:** OWASP ZAP and Burp Suite flag unencoded reflected input.

---

## 3. Stored Cross-Site Scripting (XSS)

### Vulnerability Name
Stored XSS (CWE-79)

### Vulnerable Code

```python
# Vulnerable Example - Stored XSS (unsanitized input persisted)
db.execute(
    "INSERT INTO vulnerable_comments (username, body, created_at) VALUES (?, ?, datetime('now'))",
    (username, body),
)
```

```html
{# Vulnerable Example - Stored XSS rendered without escaping #}
<div>{{ comment.body|safe }}</div>
```

**Location:** `app/routes/vulnerable.py` — `xss_stored()` and `templates/vulnerable/xss_stored.html`

Malicious HTML/JavaScript is saved to the database and rendered with the `|safe` filter.

### Attack Example

POST to `/vulnerable/xss-stored` with a comment body containing a script tag that exfiltrates cookies to an external server.

Every user who views the guestbook executes the payload persistently.

### Risk

- **Wormable attacks:** One payload affects all visitors automatically.
- **Persistent account compromise:** Unlike reflected XSS, no user interaction beyond visiting the page.
- **Admin targeting:** High-value users viewing the page are compromised.
- **Reputation damage:** Defacement and trust erosion.

---

## 4. Insecure Direct Object Reference (IDOR)

### Vulnerability Name
IDOR (CWE-639)

### Vulnerable Code

```python
# Vulnerable Example - IDOR (no ownership or authorization check)
secret = get_db().execute(
    "SELECT ... FROM user_secrets us WHERE us.id = ?",
    (secret_id,),
).fetchone()
```

**Location:** `app/routes/vulnerable.py` — `idor_secret()`

Any user can access any secret by changing the `secret_id` URL parameter. No ownership check is performed.

### Attack Example

```
GET /vulnerable/idor/secret/1
GET /vulnerable/idor/secret/2
```

An attacker enumerates IDs to retrieve admin recovery codes and API tokens.

### Risk

- **Unauthorized data access:** Exposure of private notes, documents, and credentials.
- **Horizontal privilege escalation:** Access other users' resources at the same role level.
- **Vertical privilege escalation:** Access admin-only records via predictable IDs.
- **Regulatory impact:** Unauthorized PII access triggers breach notification requirements.

---

## 5. Weak Session Management

### Vulnerability Name
Weak Session Management (CWE-384, CWE-613)

### Vulnerable Code

```python
# Vulnerable Example - Weak Session Management
session["user_id"] = int(user_id)
session["is_admin"] = is_admin
session.permanent = True
current_app.config["SESSION_COOKIE_HTTPONLY"] = False
current_app.config["SESSION_COOKIE_SECURE"] = False
current_app.config["PERMANENT_SESSION_LIFETIME"] = 86400 * 365
```

**Location:** `app/routes/vulnerable.py` — `weak_session()`

Sessions are assigned from client-supplied `user_id` without authentication. Cookie flags disable `HttpOnly` and `Secure`.

### Attack Example

1. Visit `/vulnerable/weak-session?session_id=attacker-fixed-token`
2. POST `user_id=1&is_admin=on` to assume admin identity
3. Read the non-HttpOnly cookie via JavaScript: `document.cookie`

### Risk

- **Account takeover:** Arbitrary identity assumption without credentials.
- **Session fixation:** Pre-set session IDs hijack victim sessions after login.
- **Cookie theft:** Missing `HttpOnly` allows XSS-based session stealing.
- **Man-in-the-middle:** Missing `Secure` flag exposes cookies over HTTP.

---

## 6. Hardcoded Secret

### Vulnerability Name
Hardcoded Credentials / Secrets (CWE-798)

### Vulnerable Code

```python
# Vulnerable Example - Hardcoded Secret
API_SECRET_KEY = "sk_live_hardcoded_secret_12345"
AWS_ACCESS_KEY = "AKIAEXAMPLEHARDCODEDKEY"
AWS_SECRET_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
DATABASE_PASSWORD = "SuperSecretDBPassword123!"
```

**Location:** `app/routes/vulnerable.py` and `/vulnerable/hardcoded-secret`

Secrets are embedded in source code and returned via a JSON API.

### Attack Example

```
GET /vulnerable/hardcoded-secret
```

Static analysis:

```bash
gitleaks detect --source .
bandit -r app/routes/vulnerable.py
```

### Risk

- **Cloud account compromise:** AWS keys enable resource abuse and data exfiltration.
- **API abuse:** Hardcoded API keys allow unauthorized third-party service usage.
- **Lateral movement:** Database passwords enable direct infrastructure access.
- **Supply chain exposure:** Secrets in git history persist even after deletion.

---

## 7. Security Misconfiguration

### Vulnerability Name
Security Misconfiguration (CWE-16)

### Vulnerable Code

```python
# Vulnerable Example - Security Misconfiguration
exposed = {
    "debug_mode": current_app.debug,
    "secret_key": current_app.config.get("SECRET_KEY"),
    "environment_variables": dict(os.environ),
}
```

```python
# Vulnerable Example - Security Misconfiguration (verbose error disclosure)
return f"<pre>{traceback.format_exc()}</pre>"
```

**Location:** `app/routes/vulnerable.py` — `misconfig()` and `misconfig_error()`

Debug settings, secret keys, and environment variables are exposed. Stack traces leak credentials.

### Attack Example

```
GET /vulnerable/misconfig
GET /vulnerable/misconfig/error
```

### Risk

- **Information disclosure:** Attackers map internal architecture from verbose errors.
- **Session forgery:** Exposed `SECRET_KEY` allows Flask session cookie forging.
- **Credential harvesting:** Environment variables often contain production secrets.
- **Expanded attack surface:** Debug endpoints increase exploitable surface.

---

## 8. Insecure File Upload

### Vulnerability Name
Unrestricted File Upload (CWE-434)

### Vulnerable Code

```python
# Vulnerable Example - Insecure File Upload
destination = os.path.join(VULNERABLE_UPLOAD_FOLDER, file.filename)
file.save(destination)
```

```python
# Vulnerable Example - Insecure File Upload (direct public file serving)
return send_from_directory(VULNERABLE_UPLOAD_FOLDER, filename)
```

**Location:** `app/routes/vulnerable.py` — `insecure_upload()` and `insecure_upload_serve()`

No file type validation. Original filenames preserved. Files served publicly without authentication.

### Attack Example

Upload a server-side script and request it via `/vulnerable/insecure-upload/files/<filename>`.

Path traversal via filename: `../../app.py`

### Risk

- **Remote code execution:** Executable scripts run on the server when interpreted.
- **Malware hosting:** Application becomes a distribution point for malicious files.
- **Path traversal:** Traversal in filenames can overwrite sensitive files.
- **Denial of service:** Unlimited uploads fill disk storage.

---

## Scanner Mapping

| Tool | Expected Findings |
|------|-------------------|
| **OWASP ZAP** | XSS, SQLi, IDOR, misconfiguration |
| **Bandit** | Hardcoded secrets (`B105`, `B106`) |
| **Semgrep** | SQL injection, XSS sinks, insecure upload |
| **Gitleaks** | Hardcoded AWS/API keys in source |
| **Trivy** | Misconfiguration in container/deps (when containerized) |

## Lab Index

Visit `/vulnerable/` for a linked index of all test endpoints.
