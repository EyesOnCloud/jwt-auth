import sqlite3
import os

DB_PATH = '/app/data/projects.db'

def init_db():
    os.makedirs('/app/data', exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'developer'
        )
    ''')

    # Projects table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            owner TEXT NOT NULL,
            status TEXT DEFAULT 'active',
            budget INTEGER DEFAULT 0
        )
    ''')

    # Tasks table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            assigned_to TEXT NOT NULL,
            status TEXT DEFAULT 'open',
            priority TEXT DEFAULT 'medium'
        )
    ''')

    # Seed users — IDs explicitly set so they are predictable
    users = [
        (1, 'alice',   'password123',  'admin'),
        (2, 'bob',     'bobpass',      'developer'),
        (3, 'charlie', 'charliepass',  'developer'),
    ]
    cursor.executemany(
        "INSERT OR IGNORE INTO users (id, username, password, role) VALUES (?,?,?,?)",
        users
    )

    # Seed projects
    projects = [
        (1, 'Network Upgrade',    'Upgrade core switches Q3', 'alice',   'active',  250000),
        (2, 'Security Audit',     'Annual pen test and report', 'bob',   'active',   85000),
        (3, 'Cloud Migration',    'Move legacy apps to AWS',  'charlie', 'planning', 500000),
        (4, 'Payroll System',     'Replace HR payroll system', 'alice',  'active',  175000),
    ]
    cursor.executemany(
        "INSERT OR IGNORE INTO projects (id, name, description, owner, status, budget) VALUES (?,?,?,?,?,?)",
        projects
    )

    # Seed tasks
    tasks = [
        (1, 1, 'Inventory all switches',    'bob',     'open',       'high'),
        (2, 1, 'Draft upgrade plan',        'charlie', 'in-progress','high'),
        (3, 2, 'Run vulnerability scan',    'bob',     'open',       'critical'),
        (4, 2, 'Review firewall rules',     'charlie', 'open',       'high'),
        (5, 3, 'Assess app dependencies',   'bob',     'open',       'medium'),
        (6, 4, 'Map payroll data schema',   'charlie', 'open',       'medium'),
    ]
    cursor.executemany(
        "INSERT OR IGNORE INTO tasks (id, project_id, title, assigned_to, status, priority) VALUES (?,?,?,?,?,?)",
        tasks
    )

    conn.commit()
    conn.close()
    print("[INIT] Database initialized with project management data.")

if __name__ == '__main__':
    init_db()
