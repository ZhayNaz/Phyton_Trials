import tkinter as tk
from tkinter import messagebox
import subprocess
import sys

def back_to_home():
    root.destroy()
    subprocess.Popen([sys.executable, "homeWindow.py"])

root = tk.Tk()
root.title("Computer Lab")
root.geometry("400x350")
root.configure(bg="#f0f0f0")

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = (screen_width // 2) - (400 // 2)
y = (screen_height // 2) - (350 // 2)
root.geometry(f"400x350+{x}+{y}")

tk.Label(root, text="Computer Lab", font=("Arial", 18, "bold"), bg="#f0f0f0").pack(pady=15)

frame = tk.Frame(root, bg="white", padx=20, pady=20, bd=1, relief=tk.SOLID)
frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

tk.Label(frame, text="• Lab PC 01 - Available", font=("Arial", 10), bg="white").pack(anchor="w", pady=3)
tk.Label(frame, text="• Lab PC 02 - In Use", font=("Arial", 10), bg="white").pack(anchor="w", pady=3)
tk.Label(frame, text="• Lab PC 03 - Available", font=("Arial", 10), bg="white").pack(anchor="w", pady=3)
tk.Label(frame, text="• Lab PC 04 - Offline", font=("Arial", 10), bg="white").pack(anchor="w", pady=3)

tk.Button(frame, text="⬅ Back to Home", command=back_to_home,
          bg="#2196F3", fg="white", font=("Arial", 10), width=20).pack(pady=20)

root.mainloop()
