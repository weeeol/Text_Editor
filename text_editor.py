import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from menus import configure_menus
from themes import apply_light_mode, apply_dark_mode
from text_operations import configure_text_operations
from utils import update_row_numbers, configure_event_bindings
from file_operations import new_file, open_file, save_file, save_file_as
from text_edit_operations import cut_text, copy_text, paste_text
from text_formatting import toggle_bold, toggle_italic, toggle_underline

class TextEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Text Editor")
        self.file_path = None

        # Theme attributes
        self.is_dark_mode = False
        self.light_bg = "white"
        self.light_fg = "black"
        self.dark_bg = "#2e2e2e"
        self.dark_fg = "#f8f8f2"

        # Frame and text widgets
        frame = ttk.Frame(root)
        frame.pack(expand="yes", fill="both", padx=5, pady=5)
        self.row_numbers_widget, self.main_text_widget, self.text_scrollbar = configure_text_operations(frame, self)
        self.main_text_widget.tag_configure("bold", font=("Arial", 12, "bold"))
        self.main_text_widget.tag_configure("italic", font=("Arial", 12, "italic"))
        self.main_text_widget.tag_configure("underline", underline=True)
        self.main_text_widget.bind('<KeyPress>', lambda event: self.schedule_update_row_numbers())
        self.main_text_widget.bind('<Configure>', lambda event: self.schedule_update_row_numbers())

        self.update_id = None

        # Menu bar
        self.menu_bar = configure_menus(root, self)
        

        # Event bindings
        configure_event_bindings(root, self)

        # Initial row numbers
        update_row_numbers(self)

    # File Operations
    def new_file(self):
        new_file(self)

    def open_file(self):
        open_file(self)

    def save_file(self):
        save_file(self)

    def save_file_as(self):
        save_file_as(self)

    # Theme Handlers
    def apply_light_mode(self):
        apply_light_mode(self)

    def apply_dark_mode(self):
        apply_dark_mode(self)
    
    def cut_text(self):
        cut_text(self)

    def copy_text(self):
        copy_text(self)

    def paste_text(self):
        paste_text(self)
    
    def toggle_bold(self):
        toggle_bold(self)

    def toggle_italic(self):
        toggle_italic(self)

    def toggle_underline(self):
        toggle_underline(self)
    
    def show_about_info(self):
        messagebox.showinfo("About", "Text Editor\n\nCreated by Veol Steve")

    def update_row_numbers(self):
        self.row_numbers_widget.config(state="normal")
        self.row_numbers_widget.delete(1.0, "end")

        # Calculate the number of lines
        line_count = int(self.main_text_widget.index("end-1c").split(".")[0])
        row_numbers = "\n".join(str(i) for i in range(1, line_count + 1))
        self.row_numbers_widget.insert("end", row_numbers)

        self.row_numbers_widget.config(state="disabled")
        self.row_numbers_widget.yview_moveto(self.main_text_widget.yview()[0])

    def schedule_update_row_numbers(self):
        if self.update_id:
            self.root.after_cancel(self.update_id)
        self.update_id = self.root.after(100, self.update_row_numbers)
        
    def toggle_dark_mode(self):
        if self.is_dark_mode:
            self.apply_light_mode()
        else:
            self.apply_dark_mode()

    def apply_light_mode(self):
        self.is_dark_mode = False
        self.main_text_widget.config(bg=self.light_bg, fg=self.light_fg, insertbackground=self.light_fg)
        self.row_numbers_widget.config(bg=self.light_bg, fg=self.light_fg)

    def apply_dark_mode(self):
        self.is_dark_mode = True
        self.main_text_widget.config(bg=self.dark_bg, fg=self.dark_fg, insertbackground=self.dark_fg)
        self.row_numbers_widget.config(bg=self.dark_bg, fg=self.dark_fg)