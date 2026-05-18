@echo off
echo 🛡️ Building HermitVault Executable...
echo 📦 Installing locked dependencies from requirements.txt...
pip install -r requirements.txt

echo 🚀 Starting Build Process...
python -m PyInstaller --noconsole --onefile ^
    --add-data "web;web" ^
    --add-data "logo.png;." ^
    --collect-all "zxcvbn" ^
    --collect-all "pandas" ^
    --name "HermitVault" ^
    --icon "logo.ico" ^
    main.py

echo ✅ Build Complete! Check the 'dist' folder.
pause
