# core/voice_manager.py
"""
Управление голосовыми функциями (только озвучивание)
"""

import pyttsx3
from typing import Optional
import threading

class VoiceManager:
    def __init__(self):
        self.engine = None
        self.voice_enabled = True
        self._init_engine()
    
    def _init_engine(self):
        """Инициализировать движок TTS"""
        try:
            self.engine = pyttsx3.init()
            
            # Настройки голоса
            try:
                voices = self.engine.getProperty('voices')
                if voices:
                    # Пробуем найти русский голос
                    russian_voices = [v for v in voices if 'russian' in v.name.lower() or 'ru' in v.id.lower()]
                    if russian_voices:
                        self.engine.setProperty('voice', russian_voices[0].id)
                    else:
                        self.engine.setProperty('voice', voices[0].id)
            except:
                pass  # Если не получилось настроить голос, используем по умолчанию
            
            self.engine.setProperty('rate', 150)  # Скорость речи
            self.engine.setProperty('volume', 0.9)  # Громкость
            
        except Exception as e:
            print(f"⚠️ Ошибка инициализации голосового движка: {e}")
            self.engine = None
    
    def speak(self, text: str):
        """Озвучить текст"""
        if not self.voice_enabled or not self.engine:
            return
        
        try:
            # Очищаем текст от Markdown тегов
            clean_text = self._clean_text(text)
            
            if not clean_text.strip():
                return
            
            # Озвучиваем в отдельном потоке
            def speak_thread():
                try:
                    self.engine.say(clean_text)
                    self.engine.runAndWait()
                except Exception as e:
                    print(f"Ошибка озвучивания: {e}")
            
            thread = threading.Thread(target=speak_thread, daemon=True)
            thread.start()
            
        except Exception as e:
            print(f"Ошибка подготовки речи: {e}")
    
    def _clean_text(self, text: str) -> str:
        """Очистить текст от тегов форматирования"""
        import re
        
        # Удаляем markdown теги
        clean_text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)  # Удаляем блоки кода
        clean_text = re.sub(r'`.*?`', '', clean_text)  # Удаляем inline код
        clean_text = re.sub(r'\*\*(.*?)\*\*', r'\1', clean_text)  # Удаляем жирный текст
        clean_text = re.sub(r'\*(.*?)\*', r'\1', clean_text)  # Удаляем курсив
        clean_text = re.sub(r'\[.*?\]\(.*?\)', '', clean_text)  # Удаляем ссылки
        
        # Удаляем специальные символы
        clean_text = re.sub(r'[#*_`\[\]()]', '', clean_text)
        
        # Удаляем лишние пробелы
        clean_text = re.sub(r'\s+', ' ', clean_text)
        
        return clean_text.strip()
    
    def toggle_voice(self) -> bool:
        """Переключить голосовой режим"""
        self.voice_enabled = not self.voice_enabled
        return self.voice_enabled
    
    def is_voice_enabled(self) -> bool:
        """Проверить включен ли голосовой режим"""
        return self.voice_enabled
    
    def stop(self):
        """Остановить все голосовые процессы"""
        if self.engine:
            try:
                self.engine.stop()
            except:
                pass