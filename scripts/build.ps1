# Build script using PyInstaller (Windows)
# Requires: pyinstaller installed in the Python environment

$python = "C:/Users/veols/AppData/Local/Python/pythoncore-3.14-64/python.exe"
& $python -m pip install --upgrade pyinstaller
& $python -m PyInstaller --onefile --windowed main.py
Write-Host "Build complete. See dist\main.exe"
