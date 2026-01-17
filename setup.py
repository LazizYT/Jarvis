# setup.py
"""
Скрипт установки зависимостей для Jarvis AI Assistant
"""

import subprocess
import sys
import os

def check_python():
    """Проверка версии Python"""
    print("Проверка версии Python...")
    if sys.version_info < (3, 8):
        print("❌ Требуется Python 3.8 или выше")
        return False
    print(f"✅ Python {sys.version}")
    return True

def install_requirements():
    """Установка зависимостей"""
    print("\nУстановка зависимостей...")
    
    requirements = [
        "customtkinter>=5.2.0",
        "pillow>=10.0.0",
        "requests>=2.31.0",
        "pyperclip>=1.8.2",
        "psutil>=5.9.0",
        "pyttsx3>=2.90",
        "SpeechRecognition>=3.10.0",
        "markdown>=3.5.1",
        "python-dotenv>=1.0.0"
    ]
    
    for package in requirements:
        print(f"Установка {package}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✅ {package} установлен")
        except subprocess.CalledProcessError:
            print(f"❌ Ошибка установки {package}")
            return False
    
    return True

def create_virtual_env():
    """Создание виртуального окружения"""
    print("\nСоздание виртуального окружения...")
    
    if not os.path.exists(".venv"):
        try:
            subprocess.check_call([sys.executable, "-m", "venv", ".venv"])
            print("✅ Виртуальное окружение создано")
        except subprocess.CalledProcessError:
            print("❌ Ошибка создания виртуального окружения")
            return False
    else:
        print("✅ Виртуальное окружение уже существует")
    
    return True

def print_instructions():
    """Печать инструкций"""
    print("\n" + "="*50)
    print("УСТАНОВКА ЗАВЕРШЕНА!")
    print("="*50)
    
    print("\n📋 Инструкции по запуску:")
    
    if os.name == 'nt':  # Windows
        print("\n1. Активируйте виртуальное окружение:")
        print("   .venv\\Scripts\\activate")
        print("\n2. Запустите Ollama (в отдельном терминале):")
        print("   ollama serve")
        print("\n3. Запустите Jarvis:")
        print("   python jarvis.py")
    else:  # Linux/macOS
        print("\n1. Активируйте виртуальное окружение:")
        print("   source .venv/bin/activate")
        print("\n2. Запустите Ollama (в отдельном терминале):")
        print("   ollama serve")
        print("\n3. Запустите Jarvis:")
        print("   python jarvis.py")
    
    print("\n" + "="*50)
    print("Удачи в использовании Jarvis AI Assistant! 🤖")
    print("="*50)

def main():
    """Основная функция установки"""
    print("="*50)
    print("УСТАНОВКА JARVIS AI ASSISTANT")
    print("="*50)
    
    if not check_python():
        return
    
    # Создаем виртуальное окружение
    if not create_virtual_env():
        return
    
    # Устанавливаем зависимости
    if not install_requirements():
        return
    
    # Печатаем инструкции
    print_instructions()

if __name__ == "__main__":
    main()