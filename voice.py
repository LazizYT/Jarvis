# voice.py (обновленная версия)
import pyttsx3
import threading

# Глобальная переменная для управления речью
_voice_engine = None
_speech_active = False

def init_voice_engine():
    """Инициализация голосового движка"""
    global _voice_engine
    if _voice_engine is None:
        try:
            _voice_engine = pyttsx3.init()
            # Настройки голоса
            _voice_engine.setProperty('rate', 180)  # Скорость речи
            _voice_engine.setProperty('volume', 0.9)  # Громкость
            
            # Поиск русского голоса
            voices = _voice_engine.getProperty('voices')
            for voice in voices:
                if 'russian' in voice.name.lower():
                    _voice_engine.setProperty('voice', voice.id)
                    break
            
            print("✅ Голосовой движок инициализирован")
        except Exception as e:
            print(f"❌ Ошибка инициализации голосового движка: {e}")
            _voice_engine = None
    
    return _voice_engine

def speak(text):
    """Озвучивание текста"""
    global _speech_active
    engine = init_voice_engine()
    if engine:
        try:
            _speech_active = True
            engine.say(text)
            engine.runAndWait()
            _speech_active = False
        except Exception as e:
            print(f"❌ Ошибка озвучивания: {e}")
            _speech_active = False

def stop_speech():
    """Остановить речь"""
    global _speech_active, _voice_engine
    if _voice_engine:
        try:
            _voice_engine.stop()
            _speech_active = False
            print("✅ Речь остановлена")
        except Exception as e:
            print(f"❌ Ошибка остановки речи: {e}")

def toggle_voice():
    """Переключение голоса"""
    global _voice_enabled
    _voice_enabled = not _voice_enabled
    return _voice_enabled

def is_speaking():
    """Проверка, говорит ли в данный момент"""
    return _speech_active