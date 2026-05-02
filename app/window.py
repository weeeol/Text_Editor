"""Main window for the PySide application."""

from __future__ import annotations

import os
from pathlib import Path

PYSIDE_AVAILABLE = False

try:
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QAction, QColor, QFont, QKeySequence, QPalette, QTextCharFormat
    from PySide6.QtWidgets import QApplication, QDockWidget, QFileDialog, QLabel, QMainWindow, QMessageBox, QStatusBar, QTabWidget, QToolBar
    PYSIDE_AVAILABLE = True
except Exception:
    PYSIDE_AVAILABLE = False


if PYSIDE_AVAILABLE:
    from .editor import DocumentEditor, detect_line_ending, file_type_for_path, read_text_file, write_text_file
    from .panels import FileTreePanel, SearchReplaceWidget
    from .theme import THEME_DATA, build_window_stylesheet


    class NotepadLikeWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Text Editor")
            self.resize(1200, 800)
            self._untitled_counter = 1
            self._theme_name = "dark"

            self._build_ui()
            self._build_actions()
            self._build_menus()
            self._build_toolbar()
            self._build_status_bar()
            self._build_docks()
            self.apply_theme(self._theme_name)

            self.new_tab()

        def _build_ui(self):
            self.tabs = QTabWidget()
            self.tabs.setDocumentMode(True)
            self.tabs.setTabsClosable(True)
            self.tabs.setMovable(True)
            self.tabs.setElideMode(Qt.ElideRight)
            self.tabs.setTabBarAutoHide(False)
            self.tabs.setUsesScrollButtons(True)
            tab_bar = self.tabs.tabBar()
            tab_bar.setExpanding(False)
            tab_bar.setDocumentMode(True)
            self.tabs.tabCloseRequested.connect(self.close_tab)
            self.tabs.currentChanged.connect(self._on_current_tab_changed)
            self.setCentralWidget(self.tabs)

        def _build_docks(self):
            self.search_dock = QDockWidget("Search / Replace", self)
            self.search_dock.setObjectName("searchDock")
            self.search_widget = SearchReplaceWidget(self)
            self.search_dock.setWidget(self.search_widget)
            self.search_dock.visibilityChanged.connect(self.toggle_search_action.setChecked)
            self.addDockWidget(Qt.BottomDockWidgetArea, self.search_dock)

            self.file_tree_dock = QDockWidget("File Tree", self)
            self.file_tree_dock.setObjectName("fileTreeDock")
            self.file_tree_widget = FileTreePanel(self)
            self.file_tree_dock.setWidget(self.file_tree_widget)
            self.file_tree_dock.visibilityChanged.connect(self.toggle_file_tree_action.setChecked)
            self.addDockWidget(Qt.LeftDockWidgetArea, self.file_tree_dock)

        def _build_actions(self):
            self.new_action = QAction("New", self, shortcut=QKeySequence.New, triggered=self.new_tab)
            self.open_action = QAction("Open...", self, shortcut=QKeySequence.Open, triggered=self.open_files)
            self.save_action = QAction("Save", self, shortcut=QKeySequence.Save, triggered=self.save_current)
            self.save_as_action = QAction("Save As...", self, shortcut=QKeySequence.SaveAs, triggered=self.save_current_as)
            self.close_action = QAction("Close", self, shortcut=QKeySequence.Close, triggered=self._close_current_tab)
            self.exit_action = QAction("Exit", self, triggered=self.close)

            self.undo_action = QAction("Undo", self, shortcut=QKeySequence.Undo, triggered=self._current_undo)
            self.redo_action = QAction("Redo", self, shortcut=QKeySequence.Redo, triggered=self._current_redo)
            self.cut_action = QAction("Cut", self, shortcut=QKeySequence.Cut, triggered=self._current_cut)
            self.copy_action = QAction("Copy", self, shortcut=QKeySequence.Copy, triggered=self._current_copy)
            self.paste_action = QAction("Paste", self, shortcut=QKeySequence.Paste, triggered=self._current_paste)
            self.select_all_action = QAction("Select All", self, shortcut=QKeySequence.SelectAll, triggered=self._current_select_all)

            self.bold_action = QAction("Bold", self, shortcut=QKeySequence("Ctrl+B"), triggered=self._current_toggle_bold)
            self.italic_action = QAction("Italic", self, shortcut=QKeySequence("Ctrl+I"), triggered=self._current_toggle_italic)
            self.underline_action = QAction("Underline", self, shortcut=QKeySequence("Ctrl+U"), triggered=self._current_toggle_underline)

            self.theme_toggle_action = QAction("Dark Theme", self, checkable=True, triggered=self.toggle_theme)
            self.theme_toggle_action.setChecked(True)

            self.toggle_search_action = QAction("Search / Replace", self, checkable=True, triggered=self._toggle_search_dock)
            self.toggle_search_action.setChecked(True)
            self.toggle_file_tree_action = QAction("File Tree", self, checkable=True, triggered=self._toggle_file_tree_dock)
            self.toggle_file_tree_action.setChecked(True)

            self.about_action = QAction("About", self, triggered=self.show_about)

        def _build_menus(self):
            menu_bar = self.menuBar()

            file_menu = menu_bar.addMenu("File")
            file_menu.addAction(self.new_action)
            file_menu.addAction(self.open_action)
            file_menu.addSeparator()
            file_menu.addAction(self.save_action)
            file_menu.addAction(self.save_as_action)
            file_menu.addSeparator()
            file_menu.addAction(self.close_action)
            file_menu.addSeparator()
            file_menu.addAction(self.exit_action)

            edit_menu = menu_bar.addMenu("Edit")
            edit_menu.addAction(self.undo_action)
            edit_menu.addAction(self.redo_action)
            edit_menu.addSeparator()
            edit_menu.addAction(self.cut_action)
            edit_menu.addAction(self.copy_action)
            edit_menu.addAction(self.paste_action)
            edit_menu.addAction(self.select_all_action)

            format_menu = menu_bar.addMenu("Format")
            format_menu.addAction(self.bold_action)
            format_menu.addAction(self.italic_action)
            format_menu.addAction(self.underline_action)

            view_menu = menu_bar.addMenu("View")
            view_menu.addAction(self.theme_toggle_action)
            view_menu.addAction(self.toggle_search_action)
            view_menu.addAction(self.toggle_file_tree_action)

            help_menu = menu_bar.addMenu("Help")
            help_menu.addAction(self.about_action)

        def _build_toolbar(self):
            toolbar = QToolBar("Main")
            toolbar.setMovable(False)
            toolbar.addAction(self.new_action)
            toolbar.addAction(self.open_action)
            toolbar.addAction(self.save_action)
            toolbar.addSeparator()
            toolbar.addAction(self.undo_action)
            toolbar.addAction(self.redo_action)
            toolbar.addSeparator()
            toolbar.addAction(self.cut_action)
            toolbar.addAction(self.copy_action)
            toolbar.addAction(self.paste_action)
            toolbar.addSeparator()
            toolbar.addAction(self.bold_action)
            toolbar.addAction(self.italic_action)
            toolbar.addAction(self.underline_action)
            toolbar.addSeparator()
            toolbar.addAction(self.theme_toggle_action)
            toolbar.addSeparator()
            toolbar.addAction(self.toggle_search_action)
            toolbar.addAction(self.toggle_file_tree_action)
            self.addToolBar(toolbar)

        def _build_status_bar(self):
            status = QStatusBar()
            self.setStatusBar(status)

            self.status_path = QLabel()
            self.status_encoding = QLabel()
            self.status_position = QLabel()
            self.status_mode = QLabel()
            self.status_line_ending = QLabel()
            self.status_zoom = QLabel()
            self.status_file_type = QLabel()

            for label in (self.status_path, self.status_encoding, self.status_position, self.status_mode, self.status_line_ending, self.status_zoom, self.status_file_type):
                label.setMinimumWidth(90)

            status.addPermanentWidget(self.status_path, 1)
            status.addPermanentWidget(self.status_encoding)
            status.addPermanentWidget(self.status_position)
            status.addPermanentWidget(self.status_mode)
            status.addPermanentWidget(self.status_line_ending)
            status.addPermanentWidget(self.status_zoom)
            status.addPermanentWidget(self.status_file_type)

        def current_editor(self) -> DocumentEditor | None:
            widget = self.tabs.currentWidget()
            return widget if isinstance(widget, DocumentEditor) else None

        def _new_untitled_name(self) -> str:
            name = f"Untitled {self._untitled_counter}"
            self._untitled_counter += 1
            return name

        def _wire_editor(self, editor: DocumentEditor):
            editor.cursorInfoChanged.connect(self.update_status_bar)
            editor.modeChanged.connect(self.update_status_bar)
            editor.documentStateChanged.connect(self.update_current_tab_title)
            editor.textChanged.connect(self.update_status_bar)
            editor.cursorPositionChanged.connect(editor.highlight_current_line)
            editor.zoomChanged.connect(self.update_status_bar)

        def _add_editor_tab(self, editor: DocumentEditor, title: str):
            self._wire_editor(editor)
            index = self.tabs.addTab(editor, title)
            self.tabs.setCurrentIndex(index)
            self.update_current_tab_title()
            self.update_status_bar()
            return index

        def new_tab(self):
            editor = DocumentEditor()
            editor.base_title = self._new_untitled_name()
            editor.apply_theme(self._theme_name)
            editor.setPlainText("")
            editor.document().setModified(False)
            self._add_editor_tab(editor, editor.base_title)

        def open_files(self):
            paths, _ = QFileDialog.getOpenFileNames(
                self,
                "Open Files",
                "",
                "Text Files (*.txt *.py *.md *.log);;All Files (*)",
            )
            for path in paths:
                self.open_file(path)

        def open_file(self, path: str | None = None):
            if not path:
                selected, _ = QFileDialog.getOpenFileName(
                    self,
                    "Open File",
                    "",
                    "Text Files (*.txt *.py *.md *.log);;All Files (*)",
                )
                path = selected or None

            if not path:
                return

            absolute_path = os.path.abspath(path)
            for index in range(self.tabs.count()):
                editor = self.tabs.widget(index)
                if isinstance(editor, DocumentEditor) and editor.file_path and os.path.abspath(editor.file_path) == absolute_path:
                    self.tabs.setCurrentIndex(index)
                    return

            try:
                content, encoding = read_text_file(absolute_path)
            except Exception as exc:
                QMessageBox.critical(self, "Open Failed", f"Could not open file:\n{exc}")
                return

            editor = DocumentEditor()
            editor.base_title = Path(absolute_path).name
            editor.load_text(content, absolute_path, encoding)
            editor.line_ending = detect_line_ending(content)
            editor.apply_theme(self._theme_name)
            self._add_editor_tab(editor, editor.base_title)

        def _save_editor(self, editor: DocumentEditor, path: str):
            try:
                line_ending = "\r\n" if editor.line_ending == "CRLF" else "\n"
                text = editor.toPlainText().replace("\r\n", "\n").replace("\n", line_ending)
                write_text_file(path, text, editor.encoding)
                editor.file_path = path
                editor.base_title = Path(path).name
                editor.line_ending = detect_line_ending(editor.toPlainText())
                editor.document().setModified(False)
                editor.documentStateChanged.emit()
                return True
            except Exception as exc:
                QMessageBox.critical(self, "Save Failed", f"Could not save file:\n{exc}")
                return False

        def save_current(self):
            editor = self.current_editor()
            if editor is None:
                return
            if not editor.file_path:
                self.save_current_as()
                return
            self._save_editor(editor, editor.file_path)

        def save_current_as(self):
            editor = self.current_editor()
            if editor is None:
                return
            path, _ = QFileDialog.getSaveFileName(
                self,
                "Save File As",
                editor.file_path or editor.base_title,
                "Text Files (*.txt *.py *.md *.log);;All Files (*)",
            )
            if path:
                self._save_editor(editor, path)
                self.update_current_tab_title()
                self.update_status_bar()

        def maybe_save_editor(self, editor: DocumentEditor) -> bool:
            if not editor.document().isModified():
                return True

            answer = QMessageBox.question(
                self,
                "Unsaved Changes",
                f"Save changes to {editor.base_title}?",
                QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Save,
            )
            if answer == QMessageBox.StandardButton.Save:
                if editor.file_path:
                    return self._save_editor(editor, editor.file_path)
                path, _ = QFileDialog.getSaveFileName(
                    self,
                    "Save File As",
                    editor.base_title,
                    "Text Files (*.txt *.py *.md *.log);;All Files (*)",
                )
                if not path:
                    return False
                return self._save_editor(editor, path)
            if answer == QMessageBox.StandardButton.Cancel:
                return False
            return True

        def close_tab(self, index: int):
            editor = self.tabs.widget(index)
            if not isinstance(editor, DocumentEditor):
                return
            if not self.maybe_save_editor(editor):
                return
            self.tabs.removeTab(index)
            editor.deleteLater()
            if self.tabs.count() == 0:
                self.new_tab()
            self.update_status_bar()

        def _close_current_tab(self):
            current_index = self.tabs.currentIndex()
            if current_index >= 0:
                self.close_tab(current_index)

        def closeEvent(self, event):
            for index in range(self.tabs.count() - 1, -1, -1):
                editor = self.tabs.widget(index)
                if isinstance(editor, DocumentEditor) and not self.maybe_save_editor(editor):
                    event.ignore()
                    return
            event.accept()

        def update_tab_title_for_editor(self, editor: DocumentEditor):
            index = self.tabs.indexOf(editor)
            if index < 0:
                return
            title = editor.base_title
            if editor.document().isModified():
                title += "*"
            self.tabs.setTabText(index, title)
            self.tabs.setTabToolTip(index, editor.file_path or editor.base_title)

        def update_current_tab_title(self):
            editor = self.current_editor()
            if editor is None:
                return
            self.update_tab_title_for_editor(editor)

        def _on_current_tab_changed(self, _index: int):
            editor = self.current_editor()
            if editor is not None:
                self.statusBar().showMessage(editor.file_path or editor.base_title, 2000)
                self.update_status_bar()

        def update_status_bar(self):
            editor = self.current_editor()
            if editor is None:
                self.status_path.setText("No file")
                self.status_encoding.setText("Encoding: -")
                self.status_position.setText("Ln -, Col -")
                self.status_mode.setText("INS")
                self.status_line_ending.setText("EOL: -")
                self.status_zoom.setText("Zoom: -")
                self.status_file_type.setText("Type: -")
                return

            self.update_tab_title_for_editor(editor)
            self.status_path.setText(editor.file_path or editor.base_title)
            self.status_path.setToolTip(editor.file_path or editor.base_title)
            self.status_encoding.setText(f"Encoding: {editor.encoding}")
            line, col = editor.cursor_line_column()
            self.status_position.setText(f"Ln {line}, Col {col}")
            self.status_mode.setText("OVR" if editor.is_overwrite() else "INS")
            self.status_line_ending.setText(f"EOL: {editor.line_ending}")
            self.status_zoom.setText(f"Zoom: {editor.zoom_percent}%")
            self.status_file_type.setText(f"Type: {file_type_for_path(editor.file_path)}")

        def apply_theme(self, theme_name: str):
            if theme_name not in THEME_DATA:
                return

            self._theme_name = theme_name
            theme = THEME_DATA[theme_name]

            self.theme_toggle_action.setChecked(theme_name == "dark")
            self.theme_toggle_action.setText("Dark Theme" if theme_name == "dark" else "Light Theme")

            app = QApplication.instance()
            if app is not None:
                palette = QPalette()
                palette.setColor(QPalette.Window, QColor(theme["window_bg"]))
                palette.setColor(QPalette.WindowText, QColor(theme["editor_fg"]))
                palette.setColor(QPalette.Base, QColor(theme["editor_bg"]))
                palette.setColor(QPalette.AlternateBase, QColor(theme["panel_bg"]))
                palette.setColor(QPalette.Text, QColor(theme["editor_fg"]))
                palette.setColor(QPalette.Button, QColor(theme["panel_bg"]))
                palette.setColor(QPalette.ButtonText, QColor(theme["editor_fg"]))
                palette.setColor(QPalette.Highlight, QColor(theme["selection_bg"]))
                palette.setColor(QPalette.HighlightedText, QColor(theme["selection_fg"]))
                palette.setColor(QPalette.BrightText, QColor(theme["accent"]))
                app.setPalette(palette)

            self.setStyleSheet(build_window_stylesheet(theme))

            for index in range(self.tabs.count()):
                editor = self.tabs.widget(index)
                if isinstance(editor, DocumentEditor):
                    editor.apply_theme(theme_name)
                    editor.update_line_number_area_width(0)
                    editor.highlight_current_line()

            self.update_status_bar()

        def toggle_theme(self):
            self.apply_theme("light" if self._theme_name == "dark" else "dark")

        def _toggle_search_dock(self):
            self.search_dock.setVisible(self.toggle_search_action.isChecked())

        def _toggle_file_tree_dock(self):
            self.file_tree_dock.setVisible(self.toggle_file_tree_action.isChecked())

        def show_about(self):
            QMessageBox.information(
                self,
                "About",
                "Text Editor\n\nBy Veol Steve",
            )

        def _current_undo(self):
            editor = self.current_editor()
            if editor is not None:
                editor.undo()

        def _current_redo(self):
            editor = self.current_editor()
            if editor is not None:
                editor.redo()

        def _current_cut(self):
            editor = self.current_editor()
            if editor is not None:
                editor.cut()

        def _current_copy(self):
            editor = self.current_editor()
            if editor is not None:
                editor.copy()

        def _current_paste(self):
            editor = self.current_editor()
            if editor is not None:
                editor.paste()

        def _current_select_all(self):
            editor = self.current_editor()
            if editor is not None:
                editor.selectAll()

        def _current_toggle_bold(self):
            self._apply_char_format("bold")

        def _current_toggle_italic(self):
            self._apply_char_format("italic")

        def _current_toggle_underline(self):
            self._apply_char_format("underline")

        def _apply_char_format(self, mode: str):
            editor = self.current_editor()
            if editor is None:
                return

            cursor = editor.textCursor()
            if not cursor.hasSelection():
                return

            fmt = QTextCharFormat()
            if mode == "bold":
                fmt.setFontWeight(QFont.Bold)
            elif mode == "italic":
                fmt.setFontItalic(True)
            elif mode == "underline":
                fmt.setFontUnderline(True)

            cursor.mergeCharFormat(fmt)

        def wheelEvent(self, event):
            if event.modifiers() & Qt.ControlModifier:
                editor = self.current_editor()
                if editor is not None:
                    if event.angleDelta().y() > 0:
                        editor.zoom_in()
                    else:
                        editor.zoom_out()
                    self.update_status_bar()
                    return
            super().wheelEvent(event)


    def run_pyside_app():
        app = QApplication([])
        app.setStyle("Fusion")
        window = NotepadLikeWindow()
        window.show()
        return app.exec()
