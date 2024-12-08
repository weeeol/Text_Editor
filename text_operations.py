import tkinter as tk

def configure_text_operations(frame, editor):
    text_scrollbar = tk.Scrollbar(frame, orient="vertical")
    text_scrollbar.pack(side="right", fill="y")

    row_numbers_widget = tk.Text(
        frame, width=3, wrap="none", state="disabled", bg="lightgray", fg="black", font=("Arial", 12)
    )
    row_numbers_widget.pack(side="left", fill="y")

    main_text_widget = tk.Text(
        frame, wrap="word", undo=True, yscrollcommand=text_scrollbar.set, font=("Arial", 12)
    )
    main_text_widget.pack(expand="yes", fill="both")

    text_scrollbar.config(command=main_text_widget.yview)
    main_text_widget.config(yscrollcommand=lambda *args: sync_scroll(editor, *args))

    return row_numbers_widget, main_text_widget, text_scrollbar

def sync_scroll(editor, *args):
    editor.row_numbers_widget.yview_moveto(args[0])
    editor.main_text_widget.yview_moveto(args[0])
    editor.update_row_numbers()  # Use the method from the TextEditor class