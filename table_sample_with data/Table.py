import tkinter as tk
from tkinter import ttk, messagebox
import os
import csv

CSV_FILE = "studentList.csv"

def initialize_csv():
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Name", "Age", "Course"])

def save_to_csv(name, age, course):
    with open(CSV_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([name, age, course])

def load_students():
    if os.path.exists(CSV_FILE):
        with open(CSV_FILE, mode='r') as file:
            reader = csv.reader(file)
            next(reader) 
            for row in reader:
                student_table.insert("", "end", values=row)

root = tk.Tk()
root.title("Student Table")
root.geometry("700x500")
root.configure(bg="#f5f7fa")

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = (screen_width // 2) - (700 // 2)
y = (screen_height // 2) - (500 // 2)
root.geometry(f"700x500+{x}+{y}")

style = ttk.Style()
style.theme_use("clam")
style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
style.configure("Treeview", font=("Segoe UI", 10), rowheight=28)

tk.Label(root, text="Student Records", font=("Segoe UI", 18, "bold"), bg="#f5f7fa").pack(pady=20)

form_frame = tk.Frame(root, bg="white", bd=1, relief=tk.RIDGE)
form_frame.pack(pady=10, padx=20, fill="x")

def create_input_row(row, label_text, entry_widget):
    tk.Label(form_frame, text=label_text, font=("Segoe UI", 10), bg="white", anchor="w").grid(row=row, column=0, padx=10, pady=8, sticky="w")
    entry_widget.grid(row=row, column=1, padx=10, pady=8, sticky="ew")

name_entry = ttk.Entry(form_frame, width=40)
age_entry = ttk.Entry(form_frame, width=40)
course_entry = ttk.Entry(form_frame, width=40)

form_frame.columnconfigure(1, weight=1)
create_input_row(0, "Name:", name_entry)
create_input_row(1, "Age:", age_entry)
create_input_row(2, "Course:", course_entry)

def add_student():
    name = name_entry.get().strip()
    age = age_entry.get().strip()
    course = course_entry.get().strip()

    if name and age.isdigit() and course:
        student_table.insert("", "end", values=(name, age, course))
        save_to_csv(name, age, course)
        name_entry.delete(0, tk.END)
        age_entry.delete(0, tk.END)
        course_entry.delete(0, tk.END)
    else:
        messagebox.showwarning("Input Error", "Please enter valid name, numeric age, and course.")

ttk.Button(form_frame, text="Add Student", command=add_student).grid(row=3, column=0, columnspan=2, pady=12)

table_frame = tk.Frame(root, bg="#f5f7fa")
table_frame.pack(padx=20, fill="both", expand=True)

columns = ("Name", "Age", "Course")
student_table = ttk.Treeview(table_frame, columns=columns, show="headings")
for col in columns:
    student_table.heading(col, text=col)
    student_table.column(col, anchor="center")

scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=student_table.yview)
student_table.configure(yscroll=scrollbar.set)
scrollbar.pack(side="right", fill="y")
student_table.pack(fill="both", expand=True)

initialize_csv()
load_students()

root.mainloop()
