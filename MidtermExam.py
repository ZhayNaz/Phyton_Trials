import os
import shutil
import re

def get_password(password):
    error = []
    if len(password) <8:
        error.append("Password munst be 8 characters")
    if not re.search(r"[A-Z]", password):
        error.append("Password munst have at least 1 uppercase letter")
    if not re.search(r"[a-z]", password):
        error.append("Password munst have at least 1 lowercase letter")
    if not re.search(r"\d", password):
        error.append("Password munst have at least 1 number")
    if not re.search(r"[^a-zA-Z0-9]", password):
        error.append("Password munst have at least 1 special character")
    return "password accepted!" if not error else " ".join(error)

test_cases = ["Pikachu1!", "Test@", "Laspinas2025"]

for test in test_cases:
    print(f"input: {test}, Output: {get_password(test)}")
    
def get_unique_char():
    used_char = set()
    while True:
        user_input = input("Enter string (or 'exit' to quit): ")
        if user_input.lower() == "exit":
            break
        unique_chars = set(user_input) - used_char
        if unique_chars:
            print(f"New characters: {list(unique_chars)}")
            used_char.update(unique_chars)
        else:
            print("NO new characters found.")


#desktop_path
#os.path.exists(desktop_path)


def get_files():
    last_name = "GARCIA"
    downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
    desktop_path = os.path.join(os.path.expanduser("~"),"Desktop", f"{last_name}_MIDTERMEXAM")
    if not os.path.exists(desktop_path):
        os.makedirs(desktop_path)
    files = [f for f in os.listdir(downloads_path) if os.path.isfile(os.path.join(downloads_path, f))]
    for file in files:
            src = os.path.join(downloads_path, file)
            dest = os.path.join(desktop_path, file)
            shutil.copy2(src, dest)
            print(f"file copies successfully to {desktop_path}")
