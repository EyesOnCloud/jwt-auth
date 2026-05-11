from flask import Flask, request, jsonify
import sqlite3
import os
import jwt
import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'projectapi-secret-2024'

DB_PATH = '/app/data/projects.db'


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ── AUTH HELPER ───────────────────────────────────────────────────────────────
def verify_token(request):
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return None
    token = auth_header.split(' ')[1]
    try:
        decoded = jwt.decode(
            token,
            app.config['SECRET_KEY'],
            algorithms=['HS256']   # explicit algorithm list — prevents alg:none attack
        )
        return decoded
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


# ── HEALTH CHECK ──────────────────────────────────────────────────────────────
@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "running", "message": "Project Management API"})


# ── LOGIN ─────────────────────────────────────────────────────────────────────
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400

    username = data.get('username', '')
    password = data.get('password', '')

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM users WHERE username = ? AND password = ?",
        (username, password)
    )
    user = cursor.fetchone()
    conn.close()

    if not user:
        return jsonify({"error": "Invalid credentials"}), 401

    token = jwt.encode(
        {
            'user_id':  user['id'],
            'username': user['username'],
            'role':     user['role'],
            'exp':      datetime.datetime.utcnow() + datetime.timedelta(hours=2)
        },
        app.config['SECRET_KEY'],
        algorithm='HS256'
    )
    return jsonify({"token": token, "role": user['role'], "message": "Login successful"})


# ── LIST ALL PROJECTS ──────────────────────────────────────────────────────────
@app.route('/projects', methods=['GET'])
def get_projects():
    decoded = verify_token(request)
    if not decoded:
        return jsonify({"error": "Valid token required"}), 401

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM projects")
    projects = cursor.fetchall()
    conn.close()
    return jsonify([dict(p) for p in projects])


# ── GET SINGLE PROJECT ─────────────────────────────────────────────────────────
@app.route('/projects/<int:project_id>', methods=['GET'])
def get_project(project_id):
    decoded = verify_token(request)
    if not decoded:
        return jsonify({"error": "Valid token required"}), 401

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
    project = cursor.fetchone()
    conn.close()
    if project:
        return jsonify(dict(project))
    return jsonify({"error": "Project not found"}), 404


# ── LIST TASKS FOR A PROJECT ───────────────────────────────────────────────────
@app.route('/projects/<int:project_id>/tasks', methods=['GET'])
def get_tasks(project_id):
    decoded = verify_token(request)
    if not decoded:
        return jsonify({"error": "Valid token required"}), 401

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE project_id = ?", (project_id,))
    tasks = cursor.fetchall()
    conn.close()
    return jsonify([dict(t) for t in tasks])


# ── CREATE PROJECT ─────────────────────────────────────────────────────────────
@app.route('/projects', methods=['POST'])
def create_project():
    decoded = verify_token(request)
    if not decoded:
        return jsonify({"error": "Valid token required"}), 401
    if decoded.get('role') != 'admin':
        return jsonify({"error": "Admin role required to create projects"}), 403

    data = request.get_json()
    if not data or not data.get('name'):
        return jsonify({"error": "Project name required"}), 400

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO projects (name, description, owner, status, budget) VALUES (?,?,?,?,?)",
        (data.get('name'), data.get('description', ''),
         decoded['username'], data.get('status', 'active'),
         data.get('budget', 0))
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return jsonify({"message": "Project created", "id": new_id}), 201


# ── DELETE PROJECT ─────────────────────────────────────────────────────────────
@app.route('/projects/<int:project_id>', methods=['DELETE'])
def delete_project(project_id):
    decoded = verify_token(request)
    if not decoded:
        return jsonify({"error": "Valid token required"}), 401
    if decoded.get('role') != 'admin':
        return jsonify({"error": "Admin role required to delete projects"}), 403

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM projects WHERE id = ?", (project_id,))
    conn.commit()
    conn.close()
    return jsonify({"message": f"Project {project_id} deleted"})


# ── USER PROFILE ───────────────────────────────────────────────────────────────
@app.route('/me', methods=['GET'])
def get_my_profile():
    decoded = verify_token(request)
    if not decoded:
        return jsonify({"error": "Valid token required"}), 401
    return jsonify({
        "user_id":  decoded['user_id'],
        "username": decoded['username'],
        "role":     decoded['role']
    })


# ── START ─────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
