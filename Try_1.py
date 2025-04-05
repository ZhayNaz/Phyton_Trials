import os
FILE_PATH = r"C:\Users\Mabie Garcia\Desktop\College Life\Python\credentials.txt"
def add_credentials():
    username = input("Enter Username: ")
    password = input("Enter Password: ")
    with open(FILE_PATH, "a") as file:
        file.write(f"{username},{password}\n")
        print("Credentials save successfully.")

def login():
    if not os.path.exists(FILE_PATH):
        print("No credentials found. Please add credentials first")
        return
    username = input("Enter Username: ")
    password = input("Enter Password: ")
    with open (FILE_PATH, "r") as file:
        lines = file.readlines()
        for line in lines:
            stored_user, stored_pass = line.strip().split(",")
            if stored_user == username and stored_pass == password:
                print("Login successfully!")
                return
            print("Invalid credentials. Try agian.")
 

def main():
    while True:
        print("1. Add New credentials")
        print("2. Login")
        print("0. Exit")
        choice = input("Select an option: ")
        if choice == "1":
            add_credentials()
        elif choice == "2":
            login()
        elif choice == "0":
            break
        else:
            print("Pick from the options only. [1, 2, 0]")
        continue
    
