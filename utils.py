def update_row_numbers(editor):
    # Delegate to the editor's method to avoid duplicate logic
    try:
        editor.update_row_numbers()
    except Exception:
        pass

def configure_event_bindings(root, editor):
    root.bind("<Control-n>", lambda event: editor.new_file())
    root.bind("<Control-o>", lambda event: editor.open_file())
    root.bind("<Control-s>", lambda event: editor.save_file())
    # Save As (Ctrl+Shift+S) - bind both variants for compatibility
    root.bind("<Control-Shift-s>", lambda event: editor.save_file_as())
    root.bind("<Control-Shift-S>", lambda event: editor.save_file_as())
    # Formatting shortcuts
    root.bind("<Control-b>", lambda event: editor.toggle_bold())
    root.bind("<Control-i>", lambda event: editor.toggle_italic())
    root.bind("<Control-u>", lambda event: editor.toggle_underline())
    # Undo / Redo
    root.bind("<Control-z>", lambda event: editor.main_text_widget.edit_undo())
    root.bind("<Control-y>", lambda event: editor.main_text_widget.edit_redo())
    # Ensure common cut/copy/paste work from keyboard as well
    root.bind("<Control-x>", lambda event: editor.cut_text())
    root.bind("<Control-c>", lambda event: editor.copy_text())
    root.bind("<Control-v>", lambda event: editor.paste_text())
