from flask import Flask, request, jsonify
import sqlite3
import os
import datetime

# JWT IMPLEMENTATION — import commented out, participants uncomment this
# import jwt

app = Flask(__name__)

# SECRET KEY — participants will use this when implementing JWT signing
app.config['SECRET_KEY'] = 'projectapi-secret-2024'

DB_PATH = '/app/data/projects.db'


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ── AUTH HELPER ───────────────────────────────────────────────────────────────
# This function is called by protected endpoints to verify the JWT token.
# TASK: Participants implement the body of this function.
#
# It must:
#   1. Extract the Authorization header
#   2. Check it starts with "Bearer "
#   3. Decode the token using the SECRET_KEY
#   4. Return the decoded payload
#   5. Return None if anything fails
#
def verify_token(request):
    # ── PARTICIPANTS IMPLEMENT THIS FUNCTION ──
    # Remove the line below and write your implementation
    return {"user_id": 1, "username": "bypass", "role": "admin"}  # PLACEHOLDER — no real auth


# ── HEALTH CHECK ──────────────────────────────────────────────────────────────
@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "running", "message": "Project Management API"})


# ── LOGIN ─────────────────────────────────────────────────────────────────────
# TASK: Participants implement the JWT token generation here.
#
# It must:
#   1. Parse username and password from request JSON
#   2. Query the users table with a parameterized query
#   3. If credentials match, generate a JWT with: user_id, username, role, exp
#   4. Return the token in the response
#   5. Return 401 if credentials are wrong
#
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400

    username = data.get('username', '')
    password = data.get('password', '')

    # ── PARTICIPANTS IMPLEMENT THIS SECTION ──
    # Step 1: query the database
    # Step 2: if user found, generate JWT token
    # Step 3: return token or 401

    # PLACEHOLDER — remove this block and replace with real implementation
    return jsonify({
        "message": "Login not yet implemented",
        "hint": "Query the users table, verify credentials, generate a JWT token"
    }), 501


# ── LIST ALL PROJECTS ──────────────────────────────────────────────────────────
# This endpoint should be accessible to any authenticated user.
# TASK: Add token verification — reject requests without valid token.
@app.route('/projects', methods=['GET'])
def get_projects():
    # ── PARTICIPANTS ADD TOKEN VERIFICATION HERE ──
    # Call verify_token(request) and return 401 if it returns None

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM projects")
    projects = cursor.fetchall()
    conn.close()
    return jsonify([dict(p) for p in projects])


# ── GET SINGLE PROJECT ─────────────────────────────────────────────────────────
# Accessible to any authenticated user.
# TASK: Add token verification.
@app.route('/projects/<int:project_id>', methods=['GET'])
def get_project(project_id):
    # ── PARTICIPANTS ADD TOKEN VERIFICATION HERE ──

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
    project = cursor.fetchone()
    conn.close()
    if project:
        return jsonify(dict(project))
    return jsonify({"error": "Project not found"}), 404


# ── LIST TASKS FOR A PROJECT ───────────────────────────────────────────────────
# Accessible to any authenticated user.
# TASK: Add token verification.
@app.route('/projects/<int:project_id>/tasks', methods=['GET'])
def get_tasks(project_id):
    # ── PARTICIPANTS ADD TOKEN VERIFICATION HERE ──

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE project_id = ?", (project_id,))
    tasks = cursor.fetchall()
    conn.close()
    return jsonify([dict(t) for t in tasks])


# ── CREATE PROJECT ─────────────────────────────────────────────────────────────
# Only admin users should be able to create projects.
# TASK: Add token verification AND role check — reject non-admin users with 403.
@app.route('/projects', methods=['POST'])
def create_project():
    # ── PARTICIPANTS ADD TOKEN VERIFICATION AND ROLE CHECK HERE ──

    data = request.get_json()
    if not data or not data.get('name'):
        return jsonify({"error": "Project name required"}), 400

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO projects (name, description, owner, status, budget) VALUES (?,?,?,?,?)",
        (data.get('name'), data.get('description', ''),
         data.get('owner', 'unknown'), data.get('status', 'active'),
         data.get('budget', 0))
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return jsonify({"message": "Project created", "id": new_id}), 201


# ── DELETE PROJECT ─────────────────────────────────────────────────────────────
# Only admin users should be able to delete projects.
# TASK: Add token verification AND role check.
@app.route('/projects/<int:project_id>', methods=['DELETE'])
def delete_project(project_id):
    # ── PARTICIPANTS ADD TOKEN VERIFICATION AND ROLE CHECK HERE ──

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM projects WHERE id = ?", (project_id,))
    conn.commit()
    conn.close()
    return jsonify({"message": f"Project {project_id} deleted"})


# ── USER PROFILE ───────────────────────────────────────────────────────────────
# Returns the profile of the currently logged-in user based on token claims.
# TASK: Add token verification and return profile from token payload, not URL param.
@app.route('/me', methods=['GET'])
def get_my_profile():
    # ── PARTICIPANTS ADD TOKEN VERIFICATION HERE ──
    # After verifying token, return the decoded claims as the profile
    # Do NOT accept a user_id from the URL — read it from the token only

    return jsonify({"message": "Profile endpoint not yet implemented"}), 501


# ── START ─────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
