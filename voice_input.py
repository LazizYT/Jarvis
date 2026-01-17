"""
J.A.R.V.I.S. БЕЗ PyAudio - использует sounddevice для записи
"""

import sounddevice as sd
import numpy as np
import tempfile
import scipy.io.wavfile as wav
import speech_recognition as sr
import pyttsx3
import os
import threading
import queue
from datetime import datetime
import webbrowser
import random

class JARVIS_NoPyAudio:
    def __init__(self):
        print("🚀 Инициализация J.A.R.V.I.S...")
        
        # Проверка доступных устройств
        print("🔊 Доступные аудиоустройства:")
        print(sd.query_devices())
        
        # Настройка параметров записи
        self.sample_rate = 16000
        self.channels = 1
        
        # Инициализация распознавателя речи
        self.recognizer = sr.Recognizer()
        
        # Инициализация синтезатора речи
        self.tts = pyttsx3.init()
        self.setup_voice()
        
        print("✅ J.A.R.V.I.S. готов к работе!")
    
    def setup_voice(self):
        """Настройка голоса"""
        self.tts.setProperty('rate', 180)
        self.tts.setProperty('volume', 0.9)
        
        # Ищем русский голос
        voices = self.tts.getProperty('voices')
        for voice in voices:
            if 'russian' in voice.name.lower():
                self.tts.setProperty('voice', voice.id)
                print(f"🔊 Выбран голос: {voice.name}")
                break
    
    def record_audio(self, duration=5):
        """Запись аудио через sounddevice"""
        print(f"🎤 Запись {duration} секунд...")
        
        try:
            # Запись аудио
            recording = sd.rec(
                int(duration * self.sample_rate),
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype='int16'
            )
            sd.wait()  # Ждем окончания записи
            
            print("✅ Запись завершена!")
            return recording
            
        except Exception as e:
            print(f"❌ Ошибка записи: {e}")
            return None
    
    def save_and_recognize(self, audio_data):
        """Сохранение аудио во временный файл и распознавание"""
        if audio_data is None:
            return None
        
        try:
            # Создаем временный файл
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
                # Сохраняем аудио в WAV файл
                wav.write(temp_file.name, self.sample_rate, audio_data)
                
                # Используем speech_recognition для распознавания из файла
                with sr.AudioFile(temp_file.name) as source:
                    audio = self.recognizer.record(source)
                    text = self.recognizer.recognize_google(audio, language="ru-RU")
                    
                # Удаляем временный файл
                os.unlink(temp_file.name)
                
                return text
                
        except sr.UnknownValueError:
            print("❌ Речь не распознана")
            return None
        except sr.RequestError as e:
            print(f"⚠️ Ошибка сервиса распознавания: {e}")
            return None
        except Exception as e:
            print(f"⚠️ Ошибка: {e}")
            return None
    
    def speak(self, text):
        """Озвучивание текста"""
        print(f"🤖 J.A.R.V.I.S.: {text}")
        self.tts.say(text)
        self.tts.runAndWait()
    
    def listen(self):
        """Прослушивание команды"""
        print("\n" + "="*40)
        print("🎤 СЛУШАЮ...")
        print("="*40)
        
        # Записываем аудио
        audio_data = self.record_audio(duration=5)
        
        if audio_data is not None:
            # Распознаем текст
            print("🔍 Распознаю речь...")
            text = self.save_and_recognize(audio_data)
            
            if text:
                print(f"👤 Вы сказали: {text}")
                return text.lower()
        
        return None
    
    def process_command(self, command):
        """Обработка команды"""
        if not command:
            return False
        
        command_lower = command.lower()
        
        if "привет" in command_lower:
            self.speak("Приветствую, сэр! Чем могу быть полезен?")
        
        elif any(word in command_lower for word in ["время", "который час"]):
            current_time = datetime.now().strftime("%H:%M")
            self.speak(f"Сейчас {current_time}")
        
        elif any(word in command_lower for word in ["дата", "число", "какое число"]):
            current_date = datetime.now().strftime("%d %B %Y года")
            self.speak(f"Сегодня {current_date}")
        
        elif "открой браузер" in command_lower:
            self.speak("Открываю браузер")
            webbrowser.open("https://www.google.com")
        
        elif "ютуб" in command_lower or "youtube" in command_lower:
            self.speak("Открываю YouTube")
            webbrowser.open("https://www.youtube.com")
        
        elif "погода" in command_lower:
            self.speak("Открываю прогноз погоды")
            webbrowser.open("https://yandex.ru/pogoda")
        
        elif "анекдот" in command_lower:
            jokes = [
                "Что программист сказал перед смертью? Hello World!",
                "Почему программисты не любят природу? В ней слишком много багов!",
                "Как называется программист, который не любит кофе? Java-скептик!"
            ]
            self.speak(random.choice(jokes))
        
        elif any(word in command_lower for word in ["спасибо", "благодарю"]):
            self.speak("Всегда к вашим услугам, сэр!")
        
        elif any(word in command_lower for word in ["пока", "выход", "завершить", "стоп"]):
            self.speak("До свидания, сэр! J.A.R.V.I.S. отключается.")
            return True
        
        else:
            self.speak(f"Вы сказали: {command}")
        
        return False
    
    def run_continuous(self):
        """Непрерывный режим работы"""
        self.speak("Система J.A.R.V.I.S. активирована. Ожидаю команд.")
        
        while True:
            command = self.listen()
            
            if command:
                if self.process_command(command):
                    break
    
    def run_single(self):
        """Режим одиночных команд"""
        self.speak("Режим одиночных команд активирован.")
        
        while True:
            command = self.listen()
            
            if command:
                if "выход" in command.lower() or "пока" in command.lower():
                    self.speak("До свидания!")
                    break
                self.process_command(command)

def main():
    """Главное меню"""
    print("="*50)
    print("🤖 J.A.R.V.I.S. - Just A Rather Very Intelligent System")
    print("="*50)
    print("Версия: БЕЗ PyAudio (использует sounddevice)")
    print("\nРежимы работы:")
    print("1. Непрерывное прослушивание")
    print("2. Одиночные команды")
    print("3. Тест записи звука")
    print("4. Выход")
    
    while True:
        choice = input("\nВыберите режим (1-4): ").strip()
        
        if choice == "1":
            assistant = JARVIS_NoPyAudio()
            assistant.run_continuous()
            break
        elif choice == "2":
            assistant = JARVIS_NoPyAudio()
            assistant.run_single()
            break
        elif choice == "3":
            test_recording()
            break
        elif choice == "4":
            print("👋 До свидания!")
            break
        else:
            print("❌ Неверный выбор")

def test_recording():
    """Тест записи звука"""
    print("\n" + "="*50)
    print("🎤 ТЕСТ ЗАПИСИ ЗВУКА")
    print("="*50)
    
    try:
        # Проверка устройств
        print("Доступные устройства записи:")
        devices = sd.query_devices()
        for i, device in enumerate(devices):
            if device['max_input_channels'] > 0:
                print(f"  [{i}] {device['name']}")
        
        # Запись тестового звука
        print("\n🎤 Запись тестового звука (3 секунды)...")
        recording = sd.rec(
            int(3 * 16000),
            samplerate=16000,
            channels=1,
            dtype='int16'
        )
        sd.wait()
        
        print("✅ Запись успешна!")
        print(f"📊 Размер записи: {recording.shape}")
        
        # Сохраняем в файл для проверки
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as f:
            wav.write(f.name, 16000, recording)
            print(f"💾 Аудио сохранено в: {f.name}")
        
        input("\nНажмите Enter для возврата в меню...")
        main()
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        input("\nНажмите Enter для возврата...")
        main()

if __name__ == "__main__":
    # Установите зависимости если нужно
    try:
        import sounddevice
        import scipy
        import speech_recognition
        import pyttsx3
    except ImportError:
        print("❌ Не все зависимости установлены!")
        print("Установите: pip install sounddevice scipy SpeechRecognition pyttsx3")
        exit(1)
    
    main()