"""Theme data and styling helpers for the PySide application."""

from __future__ import annotations

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
        "accent": "#007acc",
        "tab_bg": "#2d2d30",
        "tab_selected": "#1e1e1e",
        "tab_border": "#3f3f46",
        "status_bg": "#2d2d30",
        "status_fg": "#d4d4d4",
    },
}


def build_window_stylesheet(theme: dict[str, str]) -> str:
    return f"""
    QMainWindow {{ background: {theme['window_bg']}; }}
    QMenuBar {{ background: {theme['panel_bg']}; color: {theme['status_fg']}; }}
    QMenuBar::item:selected {{ background: {theme['accent']}; color: white; }}
    QMenu {{ background: {theme['panel_bg']}; color: {theme['status_fg']}; border: 1px solid {theme['tab_border']}; }}
    QMenu::item:selected {{ background: {theme['accent']}; color: white; }}
    QToolBar {{ background: {theme['panel_bg']}; border-bottom: 1px solid {theme['tab_border']}; spacing: 4px; padding: 4px; }}
    QToolButton {{ color: {theme['status_fg']}; background: transparent; border: 1px solid transparent; padding: 4px 8px; }}
    QToolButton:hover {{ background: {theme['tab_selected']}; border-color: {theme['tab_border']}; }}
    QStatusBar {{ background: {theme['status_bg']}; color: {theme['status_fg']}; border-top: 1px solid {theme['tab_border']}; }}
    QDockWidget {{ color: {theme['status_fg']}; }}
    QDockWidget::title {{ background: {theme['panel_bg']}; padding: 4px; }}
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
