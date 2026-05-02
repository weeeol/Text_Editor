"""Minimal PySide6-based UI prototype for the Text Editor.

This module is written to be import-safe when PySide6 is not installed.
If PySide6 is available it exposes `PYSIDE_AVAILABLE = True` and a
`PysideTextEditor` class to run the GUI.
"""
PYSIDE_AVAILABLE = False

try:
    from PySide6.QtWidgets import (
        QApplication,
        QMainWindow,
        QTextEdit,
        QPlainTextEdit,
        QFileDialog,
        QMessageBox,
        QAction,
        QVBoxLayout,
        QWidget,
        QHBoxLayout,
    )
    from PySide6.QtGui import QFont, QTextCharFormat, QTextCursor, QKeySequence, QPalette, QColor
    from PySide6.QtCore import Qt, Slot
    PYSIDE_AVAILABLE = True
except Exception:
    PYSIDE_AVAILABLE = False


if PYSIDE_AVAILABLE:
    # Local optional features
    try:
        from syntax_highlighter import SimplePythonHighlighter
    except Exception:
        SimplePythonHighlighter = None
    try:
        from plugins import PluginManager
    except Exception:
        PluginManager = None
    import os
    _THEMES_PATH = os.path.join(os.path.dirname(__file__), 'themes')
    class PysideTextEditor(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Text Editor (PySide6)")
            self.file_path = None

            # Central widgets
            central = QWidget()
            self.setCentralWidget(central)
            layout = QHBoxLayout(central)

            self.line_numbers = QPlainTextEdit()
            self.line_numbers.setReadOnly(True)
            self.line_numbers.setFixedWidth(50)
            self.line_numbers.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

            self.editor = QTextEdit()
            self.editor.setAcceptRichText(True)
            self.editor.setFont(QFont("Arial", 12))

            layout.addWidget(self.line_numbers)
            layout.addWidget(self.editor)

            # Connect signals
            self.editor.textChanged.connect(self.update_line_numbers)
            self.editor.cursorPositionChanged.connect(self.sync_cursor_to_line_numbers)

            # Build menus
            self._create_actions()
            self._create_menus()

            # Highlighter (optional)
            if SimplePythonHighlighter is not None:
                try:
                    self.highlighter = SimplePythonHighlighter(self.editor)
                except Exception:
                    self.highlighter = None
            else:
                self.highlighter = None

            # Plugin manager (optional)
            if PluginManager is not None:
                try:
                    self.plugin_manager = PluginManager()
                    self.plugin_manager.discover()
                    self.plugin_manager.register_all(self)
                except Exception:
                    self.plugin_manager = None
            else:
                self.plugin_manager = None

            # Default theme
            self.is_dark = False
            self.apply_light_theme()

            self.update_line_numbers()

            # Try apply theme QSS files if present
            try:
                dark_path = os.path.join(_THEMES_PATH, 'dark.qss')
                light_path = os.path.join(_THEMES_PATH, 'light.qss')
                if os.path.isfile(dark_path):
                    with open(dark_path, 'r', encoding='utf-8') as f:
                        self._dark_qss = f.read()
                else:
                    self._dark_qss = ''
                if os.path.isfile(light_path):
                    with open(light_path, 'r', encoding='utf-8') as f:
                        self._light_qss = f.read()
                else:
                    self._light_qss = ''
            except Exception:
                self._dark_qss = ''
                self._light_qss = ''

        def _create_actions(self):
            self.new_action = QAction("New", self, shortcut=QKeySequence.New, triggered=self.new_file)
            self.open_action = QAction("Open...", self, shortcut=QKeySequence.Open, triggered=self.open_file)
            self.save_action = QAction("Save", self, shortcut=QKeySequence.Save, triggered=self.save_file)
            self.save_as_action = QAction("Save As...", self, shortcut=QKeySequence.SaveAs, triggered=self.save_file_as)

            self.cut_action = QAction("Cut", self, shortcut=QKeySequence.Cut, triggered=self.editor.cut)
            self.copy_action = QAction("Copy", self, shortcut=QKeySequence.Copy, triggered=self.editor.copy)
            self.paste_action = QAction("Paste", self, shortcut=QKeySequence.Paste, triggered=self.editor.paste)

            self.bold_action = QAction("Bold", self, shortcut=QKeySequence("Ctrl+B"), triggered=self.toggle_bold)
            self.italic_action = QAction("Italic", self, shortcut=QKeySequence("Ctrl+I"), triggered=self.toggle_italic)
            self.underline_action = QAction("Underline", self, shortcut=QKeySequence("Ctrl+U"), triggered=self.toggle_underline)

            self.toggle_theme_action = QAction("Toggle Dark Mode", self, triggered=self.toggle_theme)
            self.about_action = QAction("About", self, triggered=self.show_about)

        def _create_toolbar(self):
            tb = self.addToolBar("Main")
            tb.addAction(self.new_action)
            tb.addAction(self.open_action)
            tb.addAction(self.save_action)
            tb.addSeparator()
            tb.addAction(self.cut_action)
            tb.addAction(self.copy_action)
            tb.addAction(self.paste_action)
            tb.addSeparator()
            tb.addAction(self.bold_action)
            tb.addAction(self.italic_action)
            tb.addAction(self.underline_action)
            tb.addSeparator()
            tb.addAction(self.toggle_theme_action)
            self.toolbar = tb

        def _create_menus(self):
            menu = self.menuBar()

            file_menu = menu.addMenu("File")
            file_menu.addAction(self.new_action)
            file_menu.addAction(self.open_action)
            file_menu.addAction(self.save_action)
            file_menu.addAction(self.save_as_action)

            edit_menu = menu.addMenu("Edit")
            edit_menu.addAction(self.cut_action)
            edit_menu.addAction(self.copy_action)
            edit_menu.addAction(self.paste_action)

            format_menu = menu.addMenu("Format")
            format_menu.addAction(self.bold_action)
            format_menu.addAction(self.italic_action)
            format_menu.addAction(self.underline_action)

            view_menu = menu.addMenu("View")
            view_menu.addAction(self.toggle_theme_action)

            help_menu = menu.addMenu("Help")
            help_menu.addAction(self.about_action)

            # Create toolbar after menus
            self._create_toolbar()

        def update_line_numbers(self):
            text = self.editor.toPlainText()
            lines = text.count('\n') + 1
            numbers = "\n".join(str(i) for i in range(1, lines + 1))
            self.line_numbers.setPlainText(numbers)
            # Keep scrolling in sync
            self.line_numbers.verticalScrollBar().setValue(self.editor.verticalScrollBar().value())

        def apply_qss(self, qss_text: str):
            self.setStyleSheet(qss_text)

        def sync_cursor_to_line_numbers(self):
            # Keep the line numbers scrolled to the same position
            self.line_numbers.verticalScrollBar().setValue(self.editor.verticalScrollBar().value())

        def new_file(self):
            self.editor.clear()
            self.file_path = None
            self.setWindowTitle("Text Editor (PySide6) - New File")

        def open_file(self):
            path, _ = QFileDialog.getOpenFileName(self, "Open File", "", "Text files (*.txt);;All files (*)")
            if path:
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        self.editor.setPlainText(f.read())
                    self.file_path = path
                    self.setWindowTitle(f"Text Editor (PySide6) - {path}")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to open file: {e}")

        def save_file(self):
            if not self.file_path:
                return self.save_file_as()
            try:
                with open(self.file_path, 'w', encoding='utf-8') as f:
                    f.write(self.editor.toPlainText())
                self.setWindowTitle(f"Text Editor (PySide6) - {self.file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save file: {e}")

        def save_file_as(self):
            path, _ = QFileDialog.getSaveFileName(self, "Save File As", "", "Text files (*.txt);;All files (*)")
            if path:
                self.file_path = path
                self.save_file()

        def toggle_theme(self):
            if self.is_dark:
                self.apply_light_theme()
            else:
                self.apply_dark_theme()

        def apply_light_theme(self):
            self.is_dark = False
            self.setStyleSheet("")
            palette = self.palette()
            palette.setColor(QPalette.Window, QColor("#ffffff"))
            palette.setColor(QPalette.WindowText, QColor("#000000"))
            self.setPalette(palette)

            if getattr(self, '_light_qss', ''):
                self.apply_qss(self._light_qss)

        def apply_dark_theme(self):
            self.is_dark = True
            # Simple dark stylesheet
            # Prefer loaded dark qss if available
            if getattr(self, '_dark_qss', ''):
                self.apply_qss(self._dark_qss)
            else:
                self.setStyleSheet("QTextEdit, QPlainTextEdit { background: #2e2e2e; color: #f0f0f0; }")

        def show_about(self):
            QMessageBox.information(self, "About", "Text Editor\n\nPySide6 prototype")

        def toggle_format_tag(self, tag):
            cursor = self.editor.textCursor()
            if not cursor.hasSelection():
                return
            fmt = QTextCharFormat()
            if tag == 'bold':
                fmt.setFontWeight(QFont.Bold)
            elif tag == 'italic':
                fmt.setFontItalic(True)
            elif tag == 'underline':
                fmt.setFontUnderline(True)
            cursor.mergeCharFormat(fmt)

        def toggle_bold(self):
            self.toggle_format_tag('bold')

        def toggle_italic(self):
            self.toggle_format_tag('italic')

        def toggle_underline(self):
            self.toggle_format_tag('underline')

    # Helper to run the app
    def run_pyside_app():
        app = QApplication([])
        win = PysideTextEditor()
        win.resize(900, 600)
        win.show()
        return app.exec()

else:
    # Placeholder definitions when PySide6 isn't installed
    def run_pyside_app():
        raise RuntimeError("PySide6 is not available in this environment")
