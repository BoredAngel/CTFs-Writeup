import os, sqlite3, hashlib, time
from datetime import datetime
import pytz
from flask import Flask, request, session, jsonify, send_from_directory
from flask_bcrypt import Bcrypt
from flask_cors import CORS
import subprocess
import ipaddress

DB_PATH = os.environ.get("DB_PATH", "social_media.db")

def get_conn():
    return sqlite3.connect(DB_PATH)

app = Flask(__name__)
app.secret_key = 'REDACTED' 
bcrypt = Bcrypt(app)
CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

def hash_post_id(username: str, ts: str) -> str:
    base = f"{username}-{ts}"
    return hashlib.md5(base.encode()).hexdigest()

def require_auth() -> bool:
    return 'user_id' in session and 'username' in session

def row_to_post_public(r):
    public_id = hash_post_id(r[2], r[4])
    return {
        "id": public_id,                 
        "title": r[1],
        "author": r[2],
        "content": r[3],
        "timestamp": r[4],
        "user_id": r[5]
    }

def own_post(user_id: int, post_id: int) -> bool:
    conn = get_conn(); c = conn.cursor()
    c.execute("SELECT user_id FROM posts WHERE id=?", (post_id,))
    row = c.fetchone()
    conn.close()
    return bool(row) and row[0] == user_id

def find_row_by_hid_for_current_user(hid: str):
    if not require_auth():
        return None
    conn = get_conn(); c = conn.cursor()
    c.execute("SELECT id, name, writer, content, timestamp, user_id FROM posts")
    rows = c.fetchall()
    conn.close()
    for r in rows:
        if hash_post_id(r[2], r[4]) == hid:
            return r
    return None

def find_row_hid(hid: str):
    """Resolve a hashed post id (md5(username-timestamp)) across ALL posts."""
    conn = get_conn(); c = conn.cursor()
    c.execute("SELECT id, name, writer, content, timestamp, user_id FROM posts")
    rows = c.fetchall(); conn.close()
    for r in rows:
        if hash_post_id(r[2], r[4]) == hid:
            return r
    return None

def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
      CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
      )
    """)
    c.execute("""
      CREATE TABLE IF NOT EXISTS posts(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        writer TEXT NOT NULL,
        content TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        user_id INTEGER NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(id)
      )
    """)

    c.execute("SELECT id FROM users WHERE username=?", ("admin",))
    row = c.fetchone()
    if row:
        admin_id = row[0]
    else:
        admin_pw = bcrypt.generate_password_hash("REDACTED").decode("utf-8")
        c.execute("INSERT INTO users(username,password) VALUES(?,?)", ("admin", admin_pw))
        admin_id = c.lastrowid

    c.execute('SELECT 1 FROM posts WHERE writer="admin"')
    if not c.fetchone():
        ts = str(int(time.time()))
        c.execute(
            "INSERT INTO posts(name,writer,content,timestamp,user_id) VALUES(?,?,?,?,?)",
            ("Welcome", "admin", "First post.", ts, admin_id)
        )
    c.execute("CREATE INDEX IF NOT EXISTS idx_posts_user ON posts(user_id, id DESC)")
    conn.commit()
    conn.close()

# Serve static React build
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve(path):
    if path != "" and os.path.exists("frontend/build/" + path):
        return send_from_directory("frontend/build", path)
    else:
        return send_from_directory("frontend/build", "index.html")

@app.route("/api/session", methods=["GET"])
def api_session():
    if require_auth():
        return jsonify({"authenticated": True, "username": session["username"], "user_id": session["user_id"]})
    return jsonify({"authenticated": False})

@app.route("/api/register", methods=["POST"])
def api_register():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = (data.get("password") or "").strip()
    if not username or not password:
        return jsonify({"error": "username and password required"}), 400
    conn = get_conn(); c = conn.cursor()
    c.execute("SELECT id FROM users WHERE username=?", (username,))
    if c.fetchone():
        conn.close()
        return jsonify({"error": "username already exists"}), 409
    pw = bcrypt.generate_password_hash(password).decode("utf-8")
    c.execute("INSERT INTO users(username,password) VALUES(?,?)", (username, pw))
    uid = c.lastrowid; conn.commit(); conn.close()
    session["user_id"] = uid; session["username"] = username     # auto-login
    return jsonify({"ok": True, "username": username})

@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = (data.get("password") or "").strip()
    if not username or not password:
        return jsonify({"error": "username and password required"}), 400
    conn = get_conn(); c = conn.cursor()
    c.execute("SELECT id,password FROM users WHERE username=?", (username,))
    row = c.fetchone(); conn.close()
    if row and bcrypt.check_password_hash(row[1], password):
        session["user_id"] = row[0]; session["username"] = username
        return jsonify({"ok": True, "username": username})
    return jsonify({"error": "invalid credential"}), 401

@app.route("/api/logout", methods=["POST"])
def api_logout():
    session.clear()
    return jsonify({"ok": True})

@app.route("/api/posts", methods=["GET"])
def api_posts_list():
    if not require_auth():
        return jsonify({"error": "login required"}), 401
    conn = get_conn(); c = conn.cursor()
    c.execute("SELECT id, name, writer, content, timestamp, user_id FROM posts WHERE user_id = ? ORDER BY id DESC",
              (session["user_id"],))
    rows = c.fetchall(); conn.close()
    return jsonify([row_to_post_public(r) for r in rows])

@app.route("/api/posts/<string:post_hid>", methods=["GET"])
def api_posts_get(post_hid):
    if not require_auth():
        return jsonify({"error": "login required"}), 401
    r = find_row_by_hid_for_current_user(post_hid)
    if not r:
        return jsonify({"error": "not found"}), 404
    return jsonify(row_to_post_public(r))

@app.route("/api/posts", methods=["POST"])
def api_posts_create():
    if not require_auth():
        return jsonify({"error": "login required"}), 401
    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "").strip()
    content = (data.get("content") or "").strip()
    if not title or not content:
        return jsonify({"error": "title and content required"}), 400
    ts = str(int(time.time()))
    conn = get_conn(); c = conn.cursor()
    c.execute(
        "INSERT INTO posts(name,writer,content,timestamp,user_id) VALUES(?,?,?,?,?)",
        (title, session["username"], content, ts, session["user_id"])
    )
    pid = c.lastrowid; conn.commit(); conn.close()
    public_id = hash_post_id(session["username"], ts)
    return jsonify({"id": public_id, "title": title, "author": session["username"], "content": content, "timestamp": ts}), 201

@app.route("/api/posts/<string:post_hid>", methods=["PUT", "PATCH"])
def api_posts_update(post_hid):
    if not require_auth():
        return jsonify({"error": "login required"}), 401

    r = find_row_hid(post_hid)
    if not r:
        return jsonify({"error": "not found"}), 404

    internal_id = r[0]

    data = request.get_json(silent=True) or {}
    title = data.get("title"); content = data.get("content")
    if not title and not content:
        return jsonify({"error": "nothing to update"}), 400

    ts = str(int(time.time()))
    conn = get_conn(); c = conn.cursor()
    if title and content:
        c.execute("UPDATE posts SET name=?, content=?, timestamp=? WHERE id=?", (title, content, ts, internal_id))
    elif title:
        c.execute("UPDATE posts SET name=?, timestamp=? WHERE id=?", (title, ts, internal_id))
    else:
        c.execute("UPDATE posts SET content=?, timestamp=? WHERE id=?", (content, ts, internal_id))
    conn.commit(); conn.close()

    updated_public_id = hash_post_id(r[2], ts)
    return jsonify({"ok": True, "id": updated_public_id, "timestamp": ts})

@app.route("/api/posts/<string:post_hid>", methods=["DELETE"])
def api_posts_delete(post_hid):
    if not require_auth():
        return jsonify({"error": "login required"}), 401
    r = find_row_by_hid_for_current_user(post_hid)
    if not r:
        return jsonify({"error": "not found"}), 404
    internal_id = r[0]
    if not own_post(session["user_id"], internal_id):
        return jsonify({"error": "forbidden"}), 403
    conn = get_conn(); c = conn.cursor()
    c.execute("DELETE FROM posts WHERE id=?", (internal_id,))
    conn.commit(); conn.close()
    return jsonify({"ok": True})

@app.route("/api/health", methods=["GET"])
def api_health():
    return jsonify({"ok": True, "time": int(time.time())})

@app.route("/api/admin/ping", methods=["POST"])
def api_admin_ping():
    if not require_auth():
        return jsonify({"error": "login required"}), 401
    if session["username"] != "admin":
        return jsonify({"error": "not admin"}), 403
    
    ip_str = request.remote_addr or "0.0.0.0"
    ip = ipaddress.ip_address(ip_str)

    if ip.version == 6 and ip.ipv4_mapped:
        ip = ip.ipv4_mapped

    if not (ip.is_loopback or ip.is_private):
        return jsonify({"error": "must be from localhost"}), 403
    
    data = request.get_json(silent=True) or {}
    host = data.get("host") or ""
    if not host:
        return jsonify({"error": "host required"}), 400
    try:
        output = subprocess.check_output("ping -c 1 " + host, shell=True, timeout=5)
        return jsonify({"output": output.decode("utf-8")})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=10003, debug=False)