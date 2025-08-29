# gui_viewer.py

import sqlite3
import tkinter as tk
from tkinter import ttk

DB_FILE = "lab_logs.db"

def fetch_logs():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT laboratory, action, time, date FROM logs ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()
    return rows

def refresh_table(tree):
    for row in tree.get_children():
        tree.delete(row)
    for entry in fetch_logs():
        tree.insert("", "end", values=entry)

def create_gui():
    root = tk.Tk()
    root.title("Laboratory Log Viewer")
    root.geometry("600x400")

    columns = ("Laboratory", "Action", "Time", "Date")
    tree = ttk.Treeview(root, columns=columns, show="headings")
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, anchor=tk.CENTER)

    tree.pack(fill=tk.BOTH, expand=True)

    refresh_button = tk.Button(root, text="Refresh Logs", command=lambda: refresh_table(tree))
    refresh_button.pack(pady=10)

    refresh_table(tree)
    root.mainloop()

if __name__ == "__main__":
    create_gui()