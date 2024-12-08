import tkinter as tk
from text_editor import TextEditor

if __name__ == "__main__":
    root = tk.Tk()
    app = TextEditor(root)
    root.geometry("800x600")
    root.mainloop()
