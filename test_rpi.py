import tkinter
from tkinter import *
root = tkinter.Tk()
Frame = Frame(root)
Frame.pack()
Button(Frame, text="Frame grid(row= 0, column = 0)").grid(row= 0, column = 0)
Button(Frame, text="Frame grid(row= 1, column = 1)").grid(row= 1, column = 1)
Button(root, text="pack()").pack()
Button(root, text="pady = 40").pack(pady = (40))
Button(root, text="padx = (40,0)").pack(padx = (40, 0))
Button(text = "place(x = 100, y = 200)").place(x = 100, y = 200)
Button(root, text="pack(side=left)").pack(side="left")

#root.geometry("300x200+100+50")
#button and label depends on the grid row and column
#Button(root, text="grid").grid(row= 0, column = 0)
#Label(root, text="grid").grid(row= 1, column = 1)
#print(height, width)





width = root.winfo_screenwidth()
height = root.winfo_screenheight()
root.title("sample")
root.geometry(f"{width}x{height}")
root.mainloop()


