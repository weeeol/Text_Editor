import importlib.util, traceback

spec = importlib.util.spec_from_file_location('pyside_ui','pyside_ui.py')
module = importlib.util.module_from_spec(spec)
try:
    spec.loader.exec_module(module)
    print('IMPORTED_OK', getattr(module,'PYSIDE_AVAILABLE', None))
except Exception:
    traceback.print_exc()
