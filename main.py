"""Launcher that prefers a PySide6 UI when available, falling back
to the original tkinter implementation.
"""
try:
    from pyside_ui import PYSIDE_AVAILABLE, run_pyside_app
except Exception:
    PYSIDE_AVAILABLE = False

if PYSIDE_AVAILABLE:
    if __name__ == "__main__":
        run_pyside_app()
else:
    import tkinter as tk
    from text_editor import TextEditor

    if __name__ == "__main__":
        root = tk.Tk()
        app = TextEditor(root)
        root.geometry("800x600")
        root.mainloop()
