@echo off
echo 🛡️ Building HermitVault Executable...
echo 📦 Installing PyInstaller if not present...
pip install pyinstaller

echo 🚀 Starting Build Process...
python -m PyInstaller --noconsole --onefile ^
    --add-data "web;web" ^
    --add-data "logo.png;." ^
    --name "HermitVault" ^
    --icon "logo.png" ^
    main.py

echo ✅ Build Complete! Check the 'dist' folder.
pause
