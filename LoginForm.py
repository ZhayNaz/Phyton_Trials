import tkinter as tk
from tkinter import messagebox
import sqlite3
import subprocess
import sys
from datetime import datetime

def init_db():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

init_db()

def login():
    username = username_entry.get()
    password = password_entry.get()
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    result = cursor.fetchone()

    if result:
        messagebox.showinfo("Login Success", f"Welcome, {username}!")
        login_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                login_time TEXT,
                logout_time TEXT
            )
        """)
        cursor.execute("INSERT INTO logs (username, login_time) VALUES (?, ?)", (username, login_time))
        conn.commit()
        conn.close()
        root.withdraw()
        subprocess.Popen([sys.executable, "homeWindow.py", username])  
    else:
        conn.close()
        messagebox.showerror("Login Failed", "Invalid username or password.")

def signup():
    username = username_entry.get()
    password = password_entry.get()

    if not username or not password:
        messagebox.showwarning("Input Error", "Username and password cannot be empty.")
        return

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        messagebox.showinfo("Signup Success", "User registered successfully!")
    except sqlite3.IntegrityError:
        messagebox.showerror("Signup Failed", "Username already exists.")
    finally:
        conn.close()

root = tk.Tk()
root.title("Login & Registration")
root.geometry("400x300")
root.configure(bg="#f0f0f0")

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = (screen_width // 2) - (400 // 2)
y = (screen_height // 2) - (300 // 2)
root.geometry(f"400x300+{x}+{y}")

tk.Label(root, text="Welcome", font=("Arial", 18, "bold"), bg="#f0f0f0").pack(pady=15)

frame = tk.Frame(root, bg="white", padx=20, pady=20, bd=1, relief=tk.SOLID)
frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

tk.Label(frame, text="Username:", font=("Arial", 10), bg="white").grid(row=0, column=0, sticky="w", padx=5, pady=5)
username_entry = tk.Entry(frame, width=30, font=("Arial", 10))
username_entry.grid(row=0, column=1, padx=5, pady=5)

tk.Label(frame, text="Password:", font=("Arial", 10), bg="white").grid(row=1, column=0, sticky="w", padx=5, pady=5)
password_entry = tk.Entry(frame, width=30, show="*", font=("Arial", 10))
password_entry.grid(row=1, column=1, padx=5, pady=5)

btn_frame = tk.Frame(frame, bg="white")
btn_frame.grid(row=2, column=0, columnspan=2, pady=10)

tk.Button(btn_frame, text="Login", command=login, bg="#4CAF50", fg="white", width=12, font=("Arial", 10)).pack(side="left", padx=5)
tk.Button(btn_frame, text="Signup", command=signup, bg="#2196F3", fg="white", width=12, font=("Arial", 10)).pack(side="right", padx=5)

root.mainloop()
