import sys
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

CURRENT_USER = sys.argv[1] if len(sys.argv) > 1 else "unknown"

root = tk.Tk()
root.title("User Logs")
root.geometry("600x450")
root.configure(bg="#f9f9f9")

title = tk.Label(root, text="User Login Logs", font=("Arial", 16, "bold"), bg="#f9f9f9")
title.pack(pady=10)

columns = ("username", "login_time", "logout_time")
tree = ttk.Treeview(root, columns=columns, show="headings")

tree.heading("username", text="Username")
tree.heading("login_time", text="Login Time")
tree.heading("logout_time", text="Logout Time")

tree.column("username", anchor=tk.CENTER, width=150)
tree.column("login_time", anchor=tk.CENTER, width=200)
tree.column("logout_time", anchor=tk.CENTER, width=200)

tree.pack(expand=True, fill="both", padx=20, pady=10)

def load_logs():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            login_time TEXT,
            logout_time TEXT
        )
    """)
    conn.commit()

    cursor.execute("SELECT username, login_time, logout_time FROM logs ORDER BY login_time DESC")
    logs = cursor.fetchall()
    conn.close()

    for row in tree.get_children():
        tree.delete(row)

    for log in logs:
        tree.insert("", tk.END, values=log)

load_logs()

root.mainloop()
