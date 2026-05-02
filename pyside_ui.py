"""PySide6 Notepad++-style text editor prototype.

Features:
- tabbed documents
- line numbers
- status bar with encoding, line/column, and insert/overwrite mode
- dark and light themes with a Notepad++-inspired palette
"""

from __future__ import annotations

import os
from pathlib import Path

PYSIDE_AVAILABLE = False

try:
    from PySide6.QtCore import QRect, QSize, Qt, Signal
    from PySide6.QtGui import (
        QAction,
        QColor,
        QFont,
        QKeySequence,
        QPainter,
        QPalette,
        QTextCharFormat,
        QTextCursor,
        QTextFormat,
    )
    from PySide6.QtWidgets import (
        QApplication,
        QFileDialog,
        QLabel,
        QMainWindow,
        QMenu,
        QMenuBar,
        QMessageBox,
        QPlainTextEdit,
        QStatusBar,
        QTabBar,
        QTabWidget,
        QToolBar,
        QTextEdit,
        QWidget,
    )

    PYSIDE_AVAILABLE = True
except Exception:
    PYSIDE_AVAILABLE = False


if PYSIDE_AVAILABLE:
    try:
        from syntax_highlighter import SimplePythonHighlighter
    except Exception:
        SimplePythonHighlighter = None


    THEME_DATA = {
        "light": {
            "window_bg": "#f0f0f0",
            "panel_bg": "#e7e7e7",
            "panel_alt": "#ffffff",
            "editor_bg": "#ffffff",
            "editor_fg": "#000000",
            "line_bg": "#f3f3f3",
            "line_fg": "#767676",
            "line_current": "#e8e8e8",
            "selection_bg": "#d7ebff",
            "selection_fg": "#000000",
            "caret": "#000000",
            "accent": "#0078d4",
            "tab_bg": "#dcdcdc",
            "tab_selected": "#ffffff",
            "tab_border": "#b8b8b8",
            "status_bg": "#e7e7e7",
            "status_fg": "#202020",
        },
        "dark": {
            "window_bg": "#1e1e1e",
            "panel_bg": "#252526",
            "panel_alt": "#2d2d30",
            "editor_bg": "#1e1e1e",
            "editor_fg": "#d4d4d4",
            "line_bg": "#252526",
            "line_fg": "#858585",
            "line_current": "#2a2d2e",
            "selection_bg": "#264f78",
            "selection_fg": "#ffffff",
            "caret": "#ffffff",
            "accent": "#007acc",
            "tab_bg": "#2d2d30",
            "tab_selected": "#1e1e1e",
            "tab_border": "#3f3f46",
            "status_bg": "#2d2d30",
            "status_fg": "#d4d4d4",
        },
    }


    class LineNumberArea(QWidget):
        def __init__(self, editor: "DocumentEditor"):
            super().__init__(editor)
            self._editor = editor

        def sizeHint(self):
            return QSize(self._editor.line_number_area_width(), 0)

        def paintEvent(self, event):
            self._editor.paint_line_number_area(event)


    class DocumentEditor(QPlainTextEdit):
        cursorInfoChanged = Signal()
        modeChanged = Signal()
        documentStateChanged = Signal()

        def __init__(self, parent: QWidget | None = None):
            super().__init__(parent)
            self.file_path: str | None = None
            self.encoding = "UTF-8"
            self.base_title = "Untitled"
            self._theme_name = "dark"
            self._theme = THEME_DATA[self._theme_name]
            self._highlighter = None

            self.line_number_area = LineNumberArea(self)

            self.setFont(QFont("Consolas", 11))
            self.setTabStopDistance(4 * self.fontMetrics().horizontalAdvance(" "))
            self.setOverwriteMode(False)

            self.blockCountChanged.connect(self.update_line_number_area_width)
            self.updateRequest.connect(self.update_line_number_area)
            self.cursorPositionChanged.connect(self._on_cursor_position_changed)
            self.modificationChanged.connect(lambda _modified: self.documentStateChanged.emit())

            self.update_line_number_area_width(0)
            self.highlight_current_line()
            self.apply_theme(self._theme_name)

        def sizeHint(self):
            return QSize(640, 480)

        def line_number_area_width(self) -> int:
            digits = 1
            maximum = max(1, self.blockCount())
            while maximum >= 10:
                maximum //= 10
                digits += 1
            return 8 + self.fontMetrics().horizontalAdvance("9") * digits

        def update_line_number_area_width(self, _block_count: int):
            self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

        def update_line_number_area(self, rect, dy):
            if dy:
                self.line_number_area.scroll(0, dy)
            else:
                self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())

            if rect.contains(self.viewport().rect()):
                self.update_line_number_area_width(0)

        def resizeEvent(self, event):
            super().resizeEvent(event)
            cr = self.contentsRect()
            self.line_number_area.setGeometry(QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height()))

        def paint_line_number_area(self, event):
            painter = QPainter(self.line_number_area)
            painter.fillRect(event.rect(), QColor(self._theme["line_bg"]))

            block = self.firstVisibleBlock()
            block_number = block.blockNumber()
            top = round(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
            bottom = top + round(self.blockBoundingRect(block).height())

            while block.isValid() and top <= event.rect().bottom():
                if block.isVisible() and bottom >= event.rect().top():
                    number = str(block_number + 1)
                    painter.setPen(QColor(self._theme["line_fg"]))
                    painter.drawText(
                        0,
                        top,
                        self.line_number_area.width() - 4,
                        self.fontMetrics().height(),
                        Qt.AlignRight,
                        number,
                    )

                block = block.next()
                top = bottom
                bottom = top + round(self.blockBoundingRect(block).height())
                block_number += 1

        def _on_cursor_position_changed(self):
            self.highlight_current_line()
            self.cursorInfoChanged.emit()

        def cursor_line_column(self) -> tuple[int, int]:
            cursor = self.textCursor()
            return cursor.blockNumber() + 1, cursor.positionInBlock() + 1

        def is_overwrite(self) -> bool:
            return self.overwriteMode()

        def keyPressEvent(self, event):
            if event.key() == Qt.Key_Insert:
                self.setOverwriteMode(not self.overwriteMode())
                self.modeChanged.emit()
                return
            super().keyPressEvent(event)

        def highlight_current_line(self):
            selections = []
            if not self.isReadOnly():
                selection = QTextEdit.ExtraSelection()
                line_color = QColor(self._theme["line_current"])
                line_color.setAlpha(255)
                selection.format.setBackground(line_color)
                selection.format.setProperty(QTextFormat.FullWidthSelection, True)
                selection.cursor = self.textCursor()
                selection.cursor.clearSelection()
                selections.append(selection)
            self.setExtraSelections(selections)

        def apply_theme(self, theme_name: str):
            self._theme_name = theme_name
            self._theme = THEME_DATA[theme_name]

            self.setStyleSheet(
                "QPlainTextEdit {"
                f" background: {self._theme['editor_bg']};"
                f" color: {self._theme['editor_fg']};"
                f" selection-background-color: {self._theme['selection_bg']};"
                f" selection-color: {self._theme['selection_fg']};"
                "}"
            )
            self.highlight_current_line()

            if SimplePythonHighlighter is not None:
                try:
                    if self.file_path and str(self.file_path).lower().endswith(".py"):
                        self._highlighter = SimplePythonHighlighter(self)
                    else:
                        self._highlighter = None
                except Exception:
                    self._highlighter = None

        def load_text(self, text: str, file_path: str | None = None, encoding: str = "UTF-8"):
            self.file_path = file_path
            self.encoding = encoding
            self.setPlainText(text)
            self.document().setModified(False)
            self.highlight_current_line()
            self.documentStateChanged.emit()

        def set_plain_text_safely(self, text: str):
            self.setPlainText(text)
            self.document().setModified(False)
            self.documentStateChanged.emit()


    def _read_text_file(path: str) -> tuple[str, str]:
        encodings = ("utf-8-sig", "utf-16", "cp1252")
        last_error = None
        for encoding in encodings:
            try:
                with open(path, "r", encoding=encoding) as handle:
                    return handle.read(), encoding.upper()
            except Exception as exc:
                last_error = exc
        with open(path, "r", encoding="utf-8", errors="replace") as handle:
            return handle.read(), "UTF-8"


    def _write_text_file(path: str, text: str, encoding: str):
        with open(path, "w", encoding=encoding.lower().replace("UTF-8", "utf-8"), newline="\n") as handle:
            handle.write(text)


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
            self.apply_theme(self._theme_name)

            self.new_tab()

        def _build_ui(self):
            self.tabs = QTabWidget()
            self.tabs.setDocumentMode(True)
            self.tabs.setTabsClosable(True)
            self.tabs.setMovable(True)
            self.tabs.setElideMode(Qt.ElideRight)
            self.tabs.setTabBarAutoHide(False)
            self.tabs.tabCloseRequested.connect(self.close_tab)
            self.tabs.currentChanged.connect(self._on_current_tab_changed)
            self.setCentralWidget(self.tabs)

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
            self.addToolBar(toolbar)

        def _build_status_bar(self):
            status = QStatusBar()
            self.setStatusBar(status)

            self.status_path = QLabel()
            self.status_encoding = QLabel()
            self.status_position = QLabel()
            self.status_mode = QLabel()

            for label in (self.status_path, self.status_encoding, self.status_position, self.status_mode):
                label.setMinimumWidth(90)

            status.addPermanentWidget(self.status_path, 1)
            status.addPermanentWidget(self.status_encoding)
            status.addPermanentWidget(self.status_position)
            status.addPermanentWidget(self.status_mode)

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
                content, encoding = _read_text_file(absolute_path)
            except Exception as exc:
                QMessageBox.critical(self, "Open Failed", f"Could not open file:\n{exc}")
                return

            editor = DocumentEditor()
            editor.base_title = Path(absolute_path).name
            editor.load_text(content, absolute_path, encoding)
            editor.apply_theme(self._theme_name)
            self._add_editor_tab(editor, editor.base_title)

        def _save_editor(self, editor: DocumentEditor, path: str):
            try:
                _write_text_file(path, editor.toPlainText(), editor.encoding)
                editor.file_path = path
                editor.base_title = Path(path).name
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
                return

            self.update_tab_title_for_editor(editor)
            self.status_path.setText(editor.file_path or editor.base_title)
            self.status_path.setToolTip(editor.file_path or editor.base_title)
            self.status_encoding.setText(f"Encoding: {editor.encoding}")
            line, col = editor.cursor_line_column()
            self.status_position.setText(f"Ln {line}, Col {col}")
            self.status_mode.setText("OVR" if editor.is_overwrite() else "INS")

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

            self.setStyleSheet(
                f"""
                QMainWindow {{ background: {theme['window_bg']}; }}
                QMenuBar {{ background: {theme['panel_bg']}; color: {theme['status_fg']}; }}
                QMenuBar::item:selected {{ background: {theme['accent']}; color: white; }}
                QMenu {{ background: {theme['panel_bg']}; color: {theme['status_fg']}; border: 1px solid {theme['tab_border']}; }}
                QMenu::item:selected {{ background: {theme['accent']}; color: white; }}
                QToolBar {{ background: {theme['panel_bg']}; border-bottom: 1px solid {theme['tab_border']}; spacing: 4px; padding: 4px; }}
                QToolButton {{ color: {theme['status_fg']}; background: transparent; border: 1px solid transparent; padding: 4px 8px; }}
                QToolButton:hover {{ background: {theme['tab_selected']}; border-color: {theme['tab_border']}; }}
                QStatusBar {{ background: {theme['status_bg']}; color: {theme['status_fg']}; border-top: 1px solid {theme['tab_border']}; }}
                QTabWidget::pane {{ border: 1px solid {theme['tab_border']}; top: -1px; }}
                QTabBar::tab {{
                    background: {theme['tab_bg']};
                    color: {theme['status_fg']};
                    padding: 8px 16px;
                    border: 1px solid {theme['tab_border']};
                    border-bottom: none;
                    margin-right: 2px;
                }}
                QTabBar::tab:selected {{ background: {theme['tab_selected']}; color: {theme['status_fg']}; }}
                QTabBar::tab:hover {{ background: {theme['tab_selected']}; }}
                """
            )

            for index in range(self.tabs.count()):
                editor = self.tabs.widget(index)
                if isinstance(editor, DocumentEditor):
                    editor.apply_theme(theme_name)
                    editor.update_line_number_area_width(0)
                    editor.highlight_current_line()

            self.update_status_bar()

        def toggle_theme(self):
            self.apply_theme("light" if self._theme_name == "dark" else "dark")

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


    def run_pyside_app():
        app = QApplication([])
        app.setStyle("Fusion")
        window = NotepadLikeWindow()
        window.show()
        return app.exec()


else:
    def run_pyside_app():
        raise RuntimeError("PySide6 is not available in this environment")
