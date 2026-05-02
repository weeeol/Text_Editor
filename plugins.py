import importlib.util
import os

PLUGIN_FOLDER = os.path.join(os.path.dirname(__file__), 'plugins')

class PluginManager:
    def __init__(self):
        self.plugins = {}

    def discover(self):
        if not os.path.isdir(PLUGIN_FOLDER):
            return
        for fn in os.listdir(PLUGIN_FOLDER):
            if fn.endswith('.py') and not fn.startswith('_'):
                path = os.path.join(PLUGIN_FOLDER, fn)
                name = os.path.splitext(fn)[0]
                spec = importlib.util.spec_from_file_location(name, path)
                mod = importlib.util.module_from_spec(spec)
                try:
                    spec.loader.exec_module(mod)
                    if hasattr(mod, 'register'):
                        self.plugins[name] = mod
                except Exception:
                    pass

    def register_all(self, app):
        for name, mod in self.plugins.items():
            try:
                mod.register(app)
            except Exception:
                pass
*** End Patch