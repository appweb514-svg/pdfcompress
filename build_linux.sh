#!/usr/bin/env bash
# Construit dist/pdfcompress (portable, un seul fichier) sous Linux.
# Prerequis : python3 avec tkinter (python3-tk), binutils, et pour recompiler
# le bootloader : build-essential zlib1g-dev.
set -euo pipefail
cd "$(dirname "$0")"
python3 -m venv .venv
. .venv/bin/activate
pip install --upgrade pip wheel setuptools
pip install "pymupdf>=1.24" "tkinterdnd2>=0.4"
PYINSTALLER_COMPILE_BOOTLOADER=1 pip install --no-binary pyinstaller --no-cache-dir "pyinstaller>=6.0"
pyinstaller --onefile --windowed --noupx --name pdfcompress --exclude-module PIL --exclude-module numpy --noconfirm pdfcompress.py
echo "Termine : dist/pdfcompress"
