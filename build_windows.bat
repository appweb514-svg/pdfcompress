@echo off
REM Construit pdfcompress.exe (portable, un seul fichier) et une version dossier sous Windows.
REM Prerequis : Python 3.10+ installe depuis python.org (avec Tcl/Tk, coche par defaut).
REM Pour recompiler le bootloader (moins de faux positifs antivirus), installer aussi
REM "Visual Studio Build Tools" (C++) puis decommenter la ligne set ci-dessous.
REM set PYINSTALLER_COMPILE_BOOTLOADER=1
cd /d %~dp0
py -3 -m venv .venv || python -m venv .venv
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip wheel setuptools
python -m pip install "pymupdf>=1.24" "tkinterdnd2>=0.4"
if defined PYINSTALLER_COMPILE_BOOTLOADER (
  python -m pip install --no-binary pyinstaller --no-cache-dir "pyinstaller>=6.0"
) else (
  python -m pip install "pyinstaller>=6.0"
)
set COMMON=--windowed --noupx --name pdfcompress --version-file version_info.txt --exclude-module PIL --exclude-module numpy --noconfirm --icon assets\pdfcompress.ico --add-data "assets\pdfcompress.ico;."
pyinstaller --onefile %COMMON% pdfcompress.py
pyinstaller --onedir %COMMON% --distpath dist-dir --workpath build-dir pdfcompress.py
echo.
echo Termine : dist\pdfcompress.exe (un fichier) et dist-dir\pdfcompress\ (dossier)
pause
