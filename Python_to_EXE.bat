@echo off
echo ===============================
echo CS2 WLED - Python to EXE Builder
echo ===============================

pip install -r requirements.txt
pip install pyinstaller

pyinstaller --onefile --icon=icon.ico --add-data "ip.json;." cs2_wled.py

echo.
echo Build finished!
echo EXE is in dist folder.
pause