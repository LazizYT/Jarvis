# quick_install.py
"""
Быстрая установка минимальных зависимостей
"""

import subprocess
import sys

print("Быстрая установка зависимостей для Jarvis...")

packages = [
    "customtkinter",
    "pillow", 
    "requests",
    "pyperclip"
]

for package in packages:
    print(f"Установка {package}...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

print("\n✅ Зависимости установлены!")
print("\nТеперь запустите:")
print("1. ollama serve (в отдельном терминале)")
print("2. python jarvis.py")