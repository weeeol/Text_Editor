def update_row_numbers(editor):
    editor.row_numbers_widget.config(state="normal")
    editor.row_numbers_widget.delete(1.0, "end")
    line_count = editor.main_text_widget.index("end-1c").split(".")[0]
    row_numbers = "\n".join(str(i) for i in range(1, int(line_count)))
    editor.row_numbers_widget.insert("end", row_numbers)
    editor.row_numbers_widget.config(state="disabled")

def configure_event_bindings(root, editor):
    root.bind("<Control-n>", lambda event: editor.new_file())
    root.bind("<Control-o>", lambda event: editor.open_file())
    root.bind("<Control-s>", lambda event: editor.save_file())
