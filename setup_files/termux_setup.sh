#!/data/data/com.termux/files/usr/bin/bash

if [ ! -d "/storage/emulated/0" ]; then
    echo -e "\033[93m[!] Requesting storage access. Tap ALLOW on your phone screen.\033[0m"
    termux-setup-storage
    sleep 3
fi

pkg update -y && pkg upgrade -y
pkg install tur-repo -y
pkg install clang make pkg-config libjpeg-turbo libpng freetype python python-pip python-numpy python-pillow -y

pip install setuptools wheel packaging cython

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR" || exit 1

if [ -f "setup.py" ]; then
    python setup.py
else
    python3 setup.py
fi
