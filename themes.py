def apply_light_mode(editor):
    editor.is_dark_mode = False
    editor.main_text_widget.config(bg=editor.light_bg, fg=editor.light_fg, insertbackground=editor.light_fg)
    editor.row_numbers_widget.config(bg=editor.light_bg, fg=editor.light_fg)

def apply_dark_mode(editor):
    editor.is_dark_mode = True
    editor.main_text_widget.config(bg=editor.dark_bg, fg=editor.dark_fg, insertbackground=editor.dark_fg)
    editor.row_numbers_widget.config(bg=editor.dark_bg, fg=editor.dark_fg)
