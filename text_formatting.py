def toggle_formatting(editor, tag_name):
    try:
        current_tags = editor.main_text_widget.tag_names("sel.first")
        if tag_name in current_tags:
            editor.main_text_widget.tag_remove(tag_name, "sel.first", "sel.last")
        else:
            editor.main_text_widget.tag_add(tag_name, "sel.first", "sel.last")
    except Exception:
        pass  

def toggle_bold(editor):
    toggle_formatting(editor, "bold")

def toggle_italic(editor):
    toggle_formatting(editor, "italic")

def toggle_underline(editor):
    toggle_formatting(editor, "underline")
