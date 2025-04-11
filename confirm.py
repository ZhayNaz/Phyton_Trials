# import openpyxl
# print("openpyxl is installed!")

import tkinter as tk

def open_second_window():
    second_window = tk.Toplevel(root)
    second_window.title("Second Window")
    second_window.geometry("300x200")
    
    tk.Label(second_window, text="This is the second window!", font=("Segoe UI", 12)).pack(pady=20)
    tk.Button(second_window, text="Close", command=second_window.destroy).pack()

# Main window
root = tk.Tk()
root.title("Main Window")
root.geometry("400x300")

tk.Label(root, text="Main Window", font=("Segoe UI", 16)).pack(pady=30)
tk.Button(root, text="Open Second Window", command=open_second_window).pack()

root.mainloop()
