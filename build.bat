@echo off
echo Installing PyInstaller...
pip install pyinstaller

echo Cleaning previous builds...
rmdir /s /q build dist
del /q *.spec

echo Building Executable...
pyinstaller --noconsole --onefile --name FamilyTree --clean --add-data "backups;backups" main.py

echo Build Complete.
pause
