from flask import (
    Flask, render_template, request,
    redirect, url_for, flash, jsonify
)
import sqlite3
from pathlib import Path
from datetime import datetime
from contextlib import contextmanager

# ---------------- APP CONFIGURATION ----------------

app = Flask(__name__)
app.secret_key = "recallbox-secret-key-change-later"

DATABASE = Path(__file__).resolve().parent / "recallbox.db"


# ---------------- DATABASE CONNECTION ----------------

@contextmanager
def get_db_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row

    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


# ---------------- DATABASE INITIALIZATION ----------------

def init_db():
    with get_db_connection() as connection:

        connection.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                memory_type TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL,
                is_important INTEGER DEFAULT 0
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                due_date TEXT NOT NULL,
                is_completed INTEGER DEFAULT 0,
                created_at TEXT NOT NULL
            )
        """)

        # Add missing columns without deleting existing records
        memory_columns = {
            row["name"]
            for row in connection.execute(
                "PRAGMA table_info(memories)"
            ).fetchall()
        }

        if "is_important" not in memory_columns:
            connection.execute("""
                ALTER TABLE memories
                ADD COLUMN is_important INTEGER DEFAULT 0
            """)

        reminder_columns = {
            row["name"]
            for row in connection.execute(
                "PRAGMA table_info(reminders)"
            ).fetchall()
        }

        if "is_completed" not in reminder_columns:
            connection.execute("""
                ALTER TABLE reminders
                ADD COLUMN is_completed INTEGER DEFAULT 0
            """)

        connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_memory_type
            ON memories(memory_type)
        """)

        connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_reminder_date
            ON reminders(due_date)
        """)


# ---------------- DASHBOARD ----------------

@app.route("/")
def index():

    with get_db_connection() as connection:

        memories = connection.execute("""
            SELECT * FROM memories
            ORDER BY id DESC
        """).fetchall()

        reminders = connection.execute("""
            SELECT * FROM reminders
            WHERE is_completed = 0
        """).fetchall()

    counts = {
        "total_memories": len(memories),
        "notes_count": sum(
            m["memory_type"] == "Note" for m in memories
        ),
        "links_count": sum(
            m["memory_type"] == "Link" for m in memories
        ),
        "ideas_count": sum(
            m["memory_type"] == "Idea" for m in memories
        ),
        "resources_count": sum(
            m["memory_type"] == "Resource" for m in memories
        ),
        "important_count": sum(
            m["is_important"] == 1 for m in memories
        ),
        "pending_reminders": len(reminders)
    }

    return render_template(
        "index.html",
        memories=memories,
        counts=counts,
        **counts,
        show_app=request.args.get("show_app") == "1"
    )


# ---------------- SAVE MEMORY ----------------

@app.route("/save", methods=["POST"])
def save_memory():

    title = request.form.get("title", "").strip()
    memory_type = request.form.get("memory_type", "Note").strip()
    content = request.form.get("content", "").strip()

    allowed_types = ["Note", "Link", "Idea", "Resource"]

    if not title or not content:
        flash("Please fill in all fields.", "error")
        return redirect(url_for("index", show_app=1))

    if memory_type not in allowed_types:
        memory_type = "Note"

    with get_db_connection() as connection:
        connection.execute("""
            INSERT INTO memories
            (title, memory_type, content, created_at)
            VALUES (?, ?, ?, ?)
        """, (
            title,
            memory_type,
            content,
            datetime.now().strftime("%Y-%m-%d %H:%M")
        ))

    flash("Memory saved successfully!", "success")
    return redirect(url_for("index", show_app=1))


# ---------------- EDIT MEMORY ----------------

@app.route("/edit/<int:memory_id>", methods=["POST"])
def edit_memory(memory_id):

    title = request.form.get("title", "").strip()
    memory_type = request.form.get("memory_type", "Note").strip()
    content = request.form.get("content", "").strip()

    allowed_types = ["Note", "Link", "Idea", "Resource"]

    if not title or not content:
        flash("Please fill in all fields.", "error")
        return redirect(url_for("index", show_app=1))

    if memory_type not in allowed_types:
        memory_type = "Note"

    with get_db_connection() as connection:
        connection.execute("""
            UPDATE memories
            SET title = ?, memory_type = ?, content = ?
            WHERE id = ?
        """, (title, memory_type, content, memory_id))

    flash("Memory updated successfully!", "success")
    return redirect(url_for("index", show_app=1))


# ---------------- DELETE MEMORY ----------------

@app.route("/delete/<int:memory_id>", methods=["POST"])
def delete_memory(memory_id):

    with get_db_connection() as connection:
        connection.execute("""
            DELETE FROM memories WHERE id = ?
        """, (memory_id,))

    flash("Memory deleted successfully!", "success")
    return redirect(url_for("index", show_app=1))


# ---------------- IMPORTANT MEMORY ----------------

@app.route("/toggle-important/<int:memory_id>", methods=["POST"])
def toggle_important(memory_id):

    with get_db_connection() as connection:
        connection.execute("""
            UPDATE memories
            SET is_important =
                CASE
                    WHEN is_important = 1 THEN 0
                    ELSE 1
                END
            WHERE id = ?
        """, (memory_id,))

    return redirect(url_for("index", show_app=1))


# ---------------- REMINDERS PAGE ----------------

@app.route("/reminders")
def view_reminders():

    with get_db_connection() as connection:
        reminders = connection.execute("""
            SELECT * FROM reminders
            ORDER BY is_completed ASC, due_date ASC
        """).fetchall()

    return render_template(
        "reminders.html",
        reminders=reminders
    )


# ---------------- ADD REMINDER ----------------

@app.route("/add-reminder", methods=["POST"])
def add_reminder():

    title = request.form.get("title", "").strip()
    due_date = request.form.get("due_date", "").strip()
    due_time = request.form.get("due_time", "").strip()

    if not title or not due_date or not due_time:
        flash("Please enter title, date and time.", "error")
        return redirect(url_for("view_reminders"))

    try:
        reminder_datetime = datetime.strptime(
            due_date + " " + due_time,
            "%Y-%m-%d %H:%M"
        )
    except ValueError:
        flash("Please enter a valid date and time.", "error")
        return redirect(url_for("view_reminders"))

    with get_db_connection() as connection:
        connection.execute("""
            INSERT INTO reminders
            (title, due_date, created_at)
            VALUES (?, ?, ?)
        """, (
            title,
            reminder_datetime.strftime("%Y-%m-%d %H:%M"),
            datetime.now().strftime("%Y-%m-%d %H:%M")
        ))

    flash("Reminder added successfully!", "success")
    return redirect(url_for("view_reminders"))


# ---------------- COMPLETE / REOPEN REMINDER ----------------

@app.route("/complete-reminder/<int:reminder_id>", methods=["POST"])
def complete_reminder(reminder_id):

    with get_db_connection() as connection:
        connection.execute("""
            UPDATE reminders
            SET is_completed =
                CASE
                    WHEN is_completed = 1 THEN 0
                    ELSE 1
                END
            WHERE id = ?
        """, (reminder_id,))

    return redirect(url_for("view_reminders"))


# ---------------- DELETE REMINDER ----------------

@app.route("/delete-reminder/<int:reminder_id>", methods=["POST"])
def delete_reminder(reminder_id):

    with get_db_connection() as connection:
        connection.execute("""
            DELETE FROM reminders WHERE id = ?
        """, (reminder_id,))

    flash("Reminder deleted successfully!", "success")
    return redirect(url_for("view_reminders"))


# ---------------- HEALTH CHECK ----------------

@app.route("/health")
def health():

    try:
        with get_db_connection() as connection:
            connection.execute("SELECT 1")

        return jsonify({
            "status": "success",
            "message": "RecallBox backend is running!"
        })

    except sqlite3.Error:
        return jsonify({
            "status": "error",
            "message": "Database connection failed."
        }), 500


# ---------------- ERROR HANDLING ----------------

@app.errorhandler(404)
def page_not_found(error):
    return "404 - Page not found", 404


@app.errorhandler(500)
def internal_error(error):
    return "500 - Internal server error", 500


# ---------------- START APPLICATION ----------------

init_db()

if __name__ == "__main__":
     app.run(host="0.0.0.0", port=5000, debug=False)