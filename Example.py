import tkinter as tk

root = tk.Tk()
root.geometry("600x500")
root.title("Login Form")
#screen dimension
screenWidth = root.winfo_screenwidth()
screenHeight = root.winfo_screenheight()
windowWidth = 600
windowHeight = 300
#center position
positionX = (screenWidth) // 2
positionY = (screenHeight) // 2

root.geometry(f'{windowWidth}x{windowHeight}+{positionX}+{positionY}')

    #sample widgets
    #General syntax: Widget
# Label(root, text='sample label widget').place(rely=.5, relx=.5)
# Label(root, text='sample label widget').pack(side='left')
# Label(root, text='sample label widget').grid(column=1000, row=8888)
# Label(root, text='test').grid(column=1, row=2)

#tkinter geometry managers
'''
    1. Pack --> centered / relative
    2. Grid --> tabular
    3. Place --> coordinates
'''

sampleVariable = tk.StringVar()
sampleVariable.set("Hello sa inyo.")

sampleIntVariable = tk.IntVar()
sampleIntVariable.set(1)

def button_click():
    sampleVariable.set(sampleVariable.get())
    sampleIntVariable.set(sampleIntVariable.get()+1)

def sample1():
    print(' Radio 1')

def sample2():
    print(' Radio 2')

def sample3():
    print(' Radio 3')

# Sample widget using pack
tk.Button(
    root, text='Sample pack', 
    command=button_click, 
    width=50, 
    height=10, 
    fg='RoyalBlue',
    relief='groove'
).pack()

tk.Radiobutton(
    root, text='Option 1', 
    variable=sampleIntVariable, 
    value=1, anchor='w', 
    justify='left',
    width=10,
    bg='red',
    indicator=0,
    font=('Arial', 15),
    command=sample1()
).pack()

tk.Radiobutton(
    root, text='Option 1', 
    variable=sampleIntVariable, 
    value=2, anchor='w', 
    justify='left',
    width=10,
    bg='blue',
     indicator=0,
    font=('Arial', 15)
).pack()

tk.Radiobutton(
    root, text='Option 1', 
    variable=sampleIntVariable, 
    value=3, anchor='w', 
    justify='left',
    width=10,
    indicator=0,
    font=('Arial', 15)
).pack()

root.mainloop()