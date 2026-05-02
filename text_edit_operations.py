from tkinter import messagebox


def cut_text(editor):
    try:
        editor.main_text_widget.event_generate("<<Cut>>")
    except Exception as e:
        messagebox.showerror("Error", f"Cut failed: {e}")
    editor.update_row_numbers()

def copy_text(editor):
    try:
        editor.main_text_widget.event_generate("<<Copy>>")
    except Exception as e:
        messagebox.showerror("Error", f"Copy failed: {e}")

def paste_text(editor):
    try:
        editor.main_text_widget.event_generate("<<Paste>>")
    except Exception as e:
        messagebox.showerror("Error", f"Paste failed: {e}")
    editor.update_row_numbers()
