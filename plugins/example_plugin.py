def register(app):
    # Example plugin: add a Help->Plugin menu entry
    try:
        help_menu = app.menuBar().addMenu('Plugins')
        action = help_menu.addAction('Example Plugin')
        action.triggered.connect(lambda: app.show_about())
    except Exception:
        pass
