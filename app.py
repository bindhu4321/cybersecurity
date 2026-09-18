from flask import Flask, request, render_template, jsonify
import os
import sqlite3
from markupsafe import escape

app = Flask(__name__)
DB = "secapp.db"

def init_db():
    conn = sqlite3.connect(DB)
    conn.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT)")
    conn.execute("CREATE TABLE IF NOT EXISTS feedback (id INTEGER PRIMARY KEY, message TEXT)")
    if conn.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0:
        conn.execute("INSERT INTO users(username, password) VALUES (?, ?)", ("bindhu", "demo-password"))
    conn.commit()
    conn.close()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/login", methods=["POST"])
def secure_login():
    username = request.form.get("username", "")
    password = request.form.get("password", "")
    conn = sqlite3.connect(DB)
    row = conn.execute(
        "SELECT id, username FROM users WHERE username = ? AND password = ?",
        (username, password)
    ).fetchone()
    conn.close()
    if row:
        return jsonify({"status": "success", "message": "Login successful"})
    return jsonify({"status": "error", "message": "Invalid credentials"}), 401

@app.route("/feedback", methods=["POST"])
def secure_feedback():
    message = request.form.get("message", "").strip()
    if not message or len(message) > 500:
        return jsonify({"error": "Message must contain 1–500 characters"}), 400
    safe_message = str(escape(message))
    conn = sqlite3.connect(DB)
    conn.execute("INSERT INTO feedback(message) VALUES (?)", (safe_message,))
    conn.commit()
    conn.close()
    return jsonify({"status": "saved", "message": safe_message})

@app.route("/health")
def health():
    return jsonify({"application": "SecApp Pro", "status": "running"})

if __name__ == "__main__":
    init_db()
    app.run(debug=False, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
