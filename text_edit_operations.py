def cut_text(editor):
    try:
        editor.main_text_widget.event_generate("<<Cut>>")
    except Exception as e:
        print(f"Error in cut_text: {e}")
    editor.update_row_numbers()

def copy_text(editor):
    try:
        editor.main_text_widget.event_generate("<<Copy>>")
    except Exception as e:
        print(f"Error in copy_text: {e}")

def paste_text(editor):
    try:
        editor.main_text_widget.event_generate("<<Paste>>")
    except Exception as e:
        print(f"Error in paste_text: {e}")
    editor.update_row_numbers()
