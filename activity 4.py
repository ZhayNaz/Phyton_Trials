import tkinter as tk

root = tk.Tk()

frame = tk.Frame(root, padx=20, pady=20)
frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

credentials_frame = tk.Frame(frame)
credentials_frame.pack()

username_label = tk.Label(credentials_frame, text="Username:")
username_label.grid(row=0, column=0, padx=5, pady=5)

username_entry = tk.Entry(credentials_frame, width=30)
username_entry.grid(row=0, column=1, padx=5, pady=5)

password_label = tk.Label(credentials_frame, text="Password:")
password_label.grid(row=1, column=0, padx=5, pady=5)

password_entry = tk.Entry(credentials_frame, width=30, show="*")
password_entry.grid(row=1, column=1, padx=5, pady=5)

button_frame = tk.Frame(frame)
button_frame.pack()

login_button = tk.Button(button_frame, text="Login")
login_button.grid(row=0, column=0, padx=5, pady=5)

signup_button = tk.Button(button_frame, text="Signup")
signup_button.grid(row=0, column=1, padx=5, pady=5)

root.mainloop()
