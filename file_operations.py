from tkinter import filedialog, messagebox

def new_file(editor):
    editor.main_text_widget.delete(1.0, "end")
    editor.file_path = None
    editor.root.title("Text Editor - New File")
    editor.update_row_numbers()

def open_file(editor):
    file_path = filedialog.askopenfilename(
        defaultextension=".txt", 
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
    )
    if file_path:
        try:
            with open(file_path, "r") as file:
                content = file.read()
                editor.main_text_widget.delete(1.0, "end")
                editor.main_text_widget.insert("end", content)
                editor.file_path = file_path
                editor.root.title(f"Text Editor - {file_path}")
                editor.update_row_numbers()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open file: {e}")

def save_file(editor):
    if not editor.file_path:
        save_file_as(editor)
    else:
        try:
            content = editor.main_text_widget.get(1.0, "end")
            with open(editor.file_path, "w") as file:
                file.write(content)
            editor.root.title(f"Text Editor - {editor.file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file: {e}")

def save_file_as(editor):
    file_path = filedialog.asksaveasfilename(
        defaultextension=".txt", 
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
    )
    if file_path:
        editor.file_path = file_path
        save_file(editor)
