from tkinter import Menu, messagebox

def configure_menus(root, editor):
    menu_bar = Menu(root)
    root.config(menu=menu_bar)

    # File Menu
    file_menu = Menu(menu_bar, tearoff=0)
    menu_bar.add_cascade(label="File", menu=file_menu)
    file_menu.add_command(label="New", command=editor.new_file, accelerator="Ctrl+N")
    file_menu.add_command(label="Open", command=editor.open_file, accelerator="Ctrl+O")
    file_menu.add_command(label="Save", command=editor.save_file, accelerator="Ctrl+S")
    file_menu.add_command(label="Save As", command=editor.save_file_as, accelerator="Ctrl+Shift+S")
    file_menu.add_separator()
    file_menu.add_command(label="Exit", command=root.quit)

    # Edit Menu
    edit_menu = Menu(menu_bar, tearoff=0)
    menu_bar.add_cascade(label="Edit", menu=edit_menu)
    edit_menu.add_command(label="Cut", command=editor.cut_text, accelerator="Ctrl+X")
    edit_menu.add_command(label="Copy", command=editor.copy_text, accelerator="Ctrl+C")
    edit_menu.add_command(label="Paste", command=editor.paste_text, accelerator="Ctrl+V")
    edit_menu.add_command(label="Undo", command=editor.main_text_widget.edit_undo, accelerator="Ctrl+Z")
    edit_menu.add_command(label="Redo", command=editor.main_text_widget.edit_redo, accelerator="Ctrl+Y")

    # Format Menu
    format_menu = Menu(menu_bar, tearoff=0)
    menu_bar.add_cascade(label="Format", menu=format_menu)
    format_menu.add_command(label="Bold", command=editor.toggle_bold, accelerator="Ctrl+B")
    format_menu.add_command(label="Italic", command=editor.toggle_italic, accelerator="Ctrl+I")
    format_menu.add_command(label="Underline", command=editor.toggle_underline, accelerator="Ctrl+U")

    # About Menu
    about_menu = Menu(menu_bar, tearoff=0)
    menu_bar.add_cascade(label="About", menu=about_menu)
    about_menu.add_command(label="About", command=editor.show_about_info)

    # Settings Menu (For Dark Mode)
    settings_menu = Menu(menu_bar, tearoff=0)
    menu_bar.add_cascade(label="Settings", menu=settings_menu)
    settings_menu.add_command(label="Toggle Dark Mode", command=editor.toggle_dark_mode)

    return menu_bar
