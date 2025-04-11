import tkinter as tk
from tkinter import messagebox

root = tk.Tk()
root.title("Login & Registration")
root.geometry("400x300")
root.configure(bg="#f0f0f0")

# Center the window
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = (screen_width // 2) - (400 // 2)
y = (screen_height // 2) - (300 // 2)
root.geometry(f"400x300+{x}+{y}")

# Title label
tk.Label(root, text="Welcome", font=("Arial", 18, "bold"), bg="#f0f0f0").pack(pady=10)

# Main frame
frame = tk.Frame(root, bg="white", padx=20, pady=20, bd=1, relief=tk.SOLID)
frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

# Username
tk.Label(frame, text="Username:", font=("Arial", 10), bg="white").grid(row=0, column=0, sticky="w", padx=5, pady=5)
username_entry = tk.Entry(frame, width=30, font=("Arial", 10))
username_entry.grid(row=0, column=1, padx=5, pady=5)

# Password
tk.Label(frame, text="Password:", font=("Arial", 10), bg="white").grid(row=1, column=0, sticky="w", padx=5, pady=5)
password_entry = tk.Entry(frame, width=30, show="*", font=("Arial", 10))
password_entry.grid(row=1, column=1, padx=5, pady=5)

# Button actions
def login():
    username = username_entry.get()
    password = password_entry.get()
    # Dummy check
    if username == "admin" and password == "1234":
        messagebox.showinfo("Login Success", "Welcome, admin!")
    else:
        messagebox.showerror("Login Failed", "Invalid credentials.")

def signup():
    messagebox.showinfo("Signup", "Signup functionality goes here.")

# Buttons
btn_frame = tk.Frame(frame, bg="white")
btn_frame.grid(row=2, column=0, columnspan=2, pady=10)

tk.Button(btn_frame, text="Login", command=login, bg="#4CAF50", fg="white", width=10).pack(side="left", padx=5)
tk.Button(btn_frame, text="Signup", command=signup, bg="#2196F3", fg="white", width=10).pack(side="right", padx=5)

root.mainloop()
