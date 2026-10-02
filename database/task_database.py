import sqlite3
from pathlib import Path


# Database file will live inside the database folder.
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "tasks.db"


def get_connection():
    """Create a connection to the SQLite database."""
    return sqlite3.connect(DB_PATH)


def initialize_database():
    """Create the tasks table if it doesn't already exist."""

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            due_date TEXT,
            completed INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    connection.commit()
    connection.close()


def create_task(title, due_date=None):
    """Create a new task."""

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO tasks (title, due_date)
        VALUES (?, ?)
        """,
        (title, due_date)
    )

    task_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return {
        "success": True,
        "task_id": task_id,
        "title": title,
        "due_date": due_date
    }


def list_tasks():
    """Return all tasks."""

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, title, due_date, completed, created_at
        FROM tasks
        ORDER BY id DESC
    """)

    rows = cursor.fetchall()

    connection.close()

    tasks = []

    for row in rows:

        tasks.append({
            "id": row[0],
            "title": row[1],
            "due_date": row[2],
            "completed": bool(row[3]),
            "created_at": row[4]
        })

    return tasks


def complete_task(task_id):
    """Mark a task as completed."""

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE tasks
        SET completed = 1
        WHERE id = ?
        """,
        (task_id,)
    )

    updated = cursor.rowcount

    connection.commit()
    connection.close()

    if updated == 0:
        return {
            "success": False,
            "error": "Task not found"
        }

    return {
        "success": True,
        "task_id": task_id,
        "message": "Task completed"
    }


def delete_task(task_id):
    """Delete a task."""

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        DELETE FROM tasks
        WHERE id = ?
        """,
        (task_id,)
    )

    deleted = cursor.rowcount

    connection.commit()
    connection.close()

    if deleted == 0:
        return {
            "success": False,
            "error": "Task not found"
        }

    return {
        "success": True,
        "task_id": task_id,
        "message": "Task deleted"
    }


# Initialize database when this module is loaded.
initialize_database()