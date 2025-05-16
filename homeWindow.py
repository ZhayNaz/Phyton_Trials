import tkinter as tk
import subprocess
import sys
from tkinter import messagebox
import sqlite3
from datetime import datetime

if len(sys.argv) > 1:
    CURRENT_USER = sys.argv[1]
else:
    sys.exit()

def open_computer_lab():
    subprocess.Popen([sys.executable, "ComputerLabForm.py"])

def open_chem_lab():
    subprocess.Popen([sys.executable, "ChemLabForm.py"])

def open_faculty():
    subprocess.Popen([sys.executable, "FacultyForm.py"])

def open_logs():
    subprocess.Popen([sys.executable, "LogsForm.py"])  

def logout():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    logout_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        SELECT id FROM logs
        WHERE username = ? AND logout_time IS NULL
        ORDER BY login_time DESC
        LIMIT 1
    """, (CURRENT_USER,))
    
    result = cursor.fetchone()

    if result:
        log_id = result[0]
        cursor.execute("""
            UPDATE logs
            SET logout_time = ?
            WHERE id = ?
        """, (logout_time, log_id))
        conn.commit()
        conn.close()

        messagebox.showinfo("Logout", f"{CURRENT_USER} logged out successfully.")
        root.destroy()
        subprocess.Popen([sys.executable, "LoginForm.py"])
    else:
        messagebox.showerror("Logout Error", "No active session found.")
        conn.close()

root = tk.Tk()
root.title("Home")
root.geometry("400x450")
root.configure(bg="#e6f2ff")

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = (screen_width // 2) - (400 // 2)
y = (screen_height // 2) - (450 // 2)
root.geometry(f"400x450+{x}+{y}")

title = tk.Label(root, text="Dashboard", font=("Segoe UI", 22, "bold"), bg="#e6f2ff", fg="#003366")
title.pack(pady=30)

def styled_button(master, text, command, bg="#007acc", fg="white"):
    return tk.Button(
        master, text=text, width=25, height=2,
        bg=bg, fg=fg,
        activebackground="#005f99",
        activeforeground="white",
        font=("Segoe UI", 10, "bold"),
        bd=0,
        relief="flat",
        command=command,
        cursor="hand2"
    )

styled_button(root, "🖥️  Computer Lab", open_computer_lab).pack(pady=10)
styled_button(root, "⚗️  Chem Lab", open_chem_lab).pack(pady=10)
styled_button(root, "👩‍🏫  Faculty", open_faculty).pack(pady=10)
styled_button(root, "📄  Logs", open_logs).pack(pady=10)
styled_button(root, "🚪 Logout", logout, bg="#cc0000").pack(pady=30)

root.mainloop()
