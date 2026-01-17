# gui.py (исправленная версия со всеми улучшениями)
import json
import threading
import requests
import os
import datetime
import uuid
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog
from voice import speak, toggle_voice
from markdown_parser import parse_markdown
from memory import load_memory, save_memory

# Глобальная проверка доступности библиотек для голосового ввода
VOICE_RECOGNITION_AVAILABLE = False
SOUNDDEVICE_AVAILABLE = False
SCIPY_AVAILABLE = False
VOICE_INPUT_AVAILABLE = False

try:
    import speech_recognition as sr
    VOICE_RECOGNITION_AVAILABLE = True
except ImportError:
    print("⚠️ SpeechRecognition недоступен: pip install SpeechRecognition")

try:
    import sounddevice as sd
    import numpy as np
    SOUNDDEVICE_AVAILABLE = True
except ImportError:
    print("⚠️ sounddevice недоступен: pip install sounddevice")

try:
    import scipy.io.wavfile as wav
    SCIPY_AVAILABLE = True
except ImportError:
    print("⚠️ scipy недоступен: pip install scipy")

# Проверяем полную доступность голосового ввода
if VOICE_RECOGNITION_AVAILABLE and SOUNDDEVICE_AVAILABLE and SCIPY_AVAILABLE:
    VOICE_INPUT_AVAILABLE = True
    print("✅ Голосовой ввод доступен")
else:
    print("⚠️ Голосовой ввод недоступен (установите все зависимости)")

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "llama3"

# Цветовые схемы
LIGHT_THEME = {
    "PRIMARY_COLOR": "#10a37f",
    "PRIMARY_HOVER": "#0d8c6d",
    "BACKGROUND": "#ffffff",
    "SIDEBAR_BG": "#f7f7f8",
    "CHAT_BG": "#ffffff",
    "USER_BUBBLE": "#3b82f6",  # Синий для пользователя
    "AI_BUBBLE": "#f7f7f8",    # Серый для AI
    "TEXT_PRIMARY": "#374151",
    "TEXT_SECONDARY": "#6b7280",
    "BORDER_COLOR": "#e5e7eb",
    "ACCENT_BLUE": "#3b82f6",
    "RECORDING_RED": "#dc2626",
    "RECORDING_HOVER": "#b91c1c",
    "USER_TEXT": "#ffffff",     # Белый текст на синем фоне
    "AI_TEXT": "#374151"        # Темный текст на сером фоне
}

DARK_THEME = {
    "PRIMARY_COLOR": "#10a37f",
    "PRIMARY_HOVER": "#0d8c6d",
    "BACKGROUND": "#171717",
    "SIDEBAR_BG": "#1f1f1f",
    "CHAT_BG": "#171717",
    "USER_BUBBLE": "#3b82f6",   # Синий для пользователя
    "AI_BUBBLE": "#262626",     # Темно-серый для AI
    "TEXT_PRIMARY": "#f3f4f6",
    "TEXT_SECONDARY": "#9ca3af",
    "BORDER_COLOR": "#374151",
    "ACCENT_BLUE": "#3b82f6",
    "RECORDING_RED": "#ef4444",
    "RECORDING_HOVER": "#dc2626",
    "USER_TEXT": "#ffffff",     # Белый текст на синем фоне
    "AI_TEXT": "#f3f4f6"        # Светлый текст на темном фоне
}

class JarvisApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Jarvis AI Assistant")
        self.geometry("1200x750")
        
        # Сохраняем глобальные переменные как атрибуты
        self.voice_recognition_available = VOICE_RECOGNITION_AVAILABLE
        self.sounddevice_available = SOUNDDEVICE_AVAILABLE
        self.scipy_available = SCIPY_AVAILABLE
        self.voice_input_available = VOICE_INPUT_AVAILABLE
        
        # Загружаем память
        self.memory = load_memory()
        self.current_theme = self.memory.get("settings", {}).get("theme", "light")
        
        # Устанавливаем тему
        self.colors = LIGHT_THEME if self.current_theme == "light" else DARK_THEME
        ctk.set_appearance_mode(self.current_theme)
        ctk.set_default_color_theme("blue")
        
        # Переменные для голосового ввода
        self.is_recording = False
        self.recognizer = None
        self.fs = 16000  # частота дискретизации для записи
        self.recording_duration = 5  # длительность записи в секундах
        
        # Инициализируем распознаватель речи если доступно
        if self.voice_input_available:
            try:
                self.recognizer = sr.Recognizer()
                print("✅ Голосовой ввод инициализирован")
            except Exception as e:
                print(f"⚠️ Ошибка инициализации голосового ввода: {e}")
                self.voice_input_available = False
        
        # Переменные
        self.think_mode = False
        self.current_chat = []
        self.current_chat_id = None
        self.sidebar_visible = True
        self.chat_buttons = {}
        self.voice_enabled = True
        self.is_streaming = False
        self.is_jarvis_speaking = False  # Флаг что Jarvis говорит
        self.thinking_animation_active = False  # Флаг анимации мышления
        
        # Центрируем окно
        self.center_window()
        
        # Создаем интерфейс
        self.create_widgets()
        
        # Загружаем историю
        self.load_chat_history()
        
        # Настраиваем закрытие
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def center_window(self):
        """Центрировать окно"""
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - 1200) // 2
        y = (screen_height - 750) // 2
        self.geometry(f"1200x750+{x}+{y}")
    
    def create_widgets(self):
        """Создать все виджеты"""
        # ================= SIDEBAR =================
        self.sidebar = ctk.CTkFrame(
            self, 
            width=260, 
            fg_color=self.colors["SIDEBAR_BG"],
            corner_radius=0
        )
        self.sidebar.pack(side="left", fill="y")
        
        # Логотип и новая беседа
        logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        logo_frame.pack(fill="x", padx=12, pady=(16, 8))
        
        self.new_chat_btn = ctk.CTkButton(
            logo_frame,
            text="🆕 new chat",
            width=220,
            height=40,
            fg_color=self.colors["PRIMARY_COLOR"],
            hover_color=self.colors["PRIMARY_HOVER"],
            text_color="white",
            font=("Segoe UI", 13, "bold"),
            corner_radius=8,
            command=self.new_chat
        )
        self.new_chat_btn.pack(pady=(0, 16))
        
        # История чатов
        history_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        history_frame.pack(fill="x", padx=12, pady=(0, 16))
        
        history_header = ctk.CTkFrame(history_frame, fg_color="transparent")
        history_header.pack(fill="x", pady=(0, 8))
        
        ctk.CTkLabel(
            history_header,
            text="History",
            font=("Segoe UI", 12, "bold"),
            text_color=self.colors["TEXT_PRIMARY"]
        ).pack(side="left")
        
        # Кнопка очистки истории
        ctk.CTkButton(
            history_header,
            text="🗑️",
            width=30,
            height=24,
            fg_color="transparent",
            hover_color="#e5e5e5" if self.current_theme == "light" else "#374151",
            text_color=self.colors["TEXT_SECONDARY"],
            font=("Segoe UI", 12),
            command=self.clear_all_history
        ).pack(side="right")
        
        # Список чатов с ПРАВИЛЬНОЙ прокруткой
        self.chat_list_scroll = ctk.CTkScrollableFrame(
            history_frame,
            fg_color="transparent",
            height=380,
            scrollbar_button_color="#c1c1c1" if self.current_theme == "light" else "#4b5563",
            scrollbar_button_hover_color="#a1a1a1" if self.current_theme == "light" else "#374151"
        )
        self.chat_list_scroll.pack(fill="both", expand=True)
        self.chat_list_scroll._parent_canvas.configure(highlightthickness=0)
        
        # Нижняя часть сайдбара
        bottom_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        bottom_frame.pack(side="bottom", fill="x", padx=12, pady=16)
        
        # Кнопка смены темы
        self.theme_btn = ctk.CTkButton(
            bottom_frame,
            text="🌙 Theme" if self.current_theme == "light" else "☀️ Theme",
            width=220,
            height=40,
            fg_color=self.colors["BACKGROUND"],
            hover_color=self.colors["USER_BUBBLE"],
            text_color=self.colors["TEXT_PRIMARY"],
            font=("Segoe UI", 12),
            anchor="w",
            corner_radius=8,
            command=self.toggle_theme
        )
        self.theme_btn.pack(fill="x", pady=(0, 10))
        
        # Кнопка пользователя с иконкой
        user_btn_frame = ctk.CTkFrame(bottom_frame, fg_color="transparent")
        user_btn_frame.pack(fill="x")
        
        # Иконка пользователя
        ctk.CTkLabel(
            user_btn_frame,
            text="👤",
            font=("Segoe UI", 16),
            text_color=self.colors["TEXT_PRIMARY"],
            width=30
        ).pack(side="left")
        
        # Имя пользователя
        ctk.CTkLabel(
            user_btn_frame,
            text="User Account",
            font=("Segoe UI", 12),
            text_color=self.colors["TEXT_PRIMARY"]
        ).pack(side="left", padx=(10, 0))
        
        # ================= CHAT AREA =================
        self.main_frame = ctk.CTkFrame(self, fg_color=self.colors["CHAT_BG"])
        self.main_frame.pack(side="right", fill="both", expand=True)
        
        # Верхняя панель
        top_bar = ctk.CTkFrame(
            self.main_frame,
            height=60,
            fg_color=self.colors["CHAT_BG"],
            corner_radius=0
        )
        top_bar.pack(fill="x", padx=20, pady=(10, 0))
        
        # Заголовок чата
        self.chat_title = ctk.CTkLabel(
            top_bar,
            text="New chat",
            font=("Segoe UI", 18, "bold"),
            text_color=self.colors["TEXT_PRIMARY"]
        )
        self.chat_title.pack(side="left")
        
        # Кнопки управления
        control_frame = ctk.CTkFrame(top_bar, fg_color="transparent")
        control_frame.pack(side="right")
        
        # Кнопка сайдбара
        self.sidebar_toggle_btn = ctk.CTkButton(
            control_frame,
            text="☰",
            width=36,
            height=36,
            fg_color="transparent",
            hover_color=self.colors["USER_BUBBLE"],
            text_color=self.colors["TEXT_PRIMARY"],
            font=("Segoe UI", 16),
            command=self.toggle_sidebar
        )
        self.sidebar_toggle_btn.pack(side="left", padx=5)
        
        # Кнопка голоса (воспроизведение) - теперь с возможностью остановки
        self.voice_btn = ctk.CTkButton(
            control_frame,
            text="🔊",
            width=36,
            height=36,
            fg_color="transparent",
            hover_color=self.colors["USER_BUBBLE"],
            text_color=self.colors["TEXT_PRIMARY"],
            font=("Segoe UI", 16),
            command=self.toggle_voice_ui
        )
        self.voice_btn.pack(side="left", padx=5)
        
        # Кнопка загрузки файла
        self.upload_btn = ctk.CTkButton(
            control_frame,
            text="📎",
            width=36,
            height=36,
            fg_color="transparent",
            hover_color=self.colors["USER_BUBBLE"],
            text_color=self.colors["TEXT_PRIMARY"],
            font=("Segoe UI", 16),
            command=self.upload_file
        )
        self.upload_btn.pack(side="left", padx=5)
        
        # ================= CHAT CONTAINER =================
        # Сразу создаем scrollable frame для чата
        self.chat_scroll = ctk.CTkScrollableFrame(
            self.main_frame,
            fg_color=self.colors["CHAT_BG"],
            scrollbar_button_color="#c1c1c1" if self.current_theme == "light" else "#4b5563",
            scrollbar_button_hover_color="#a1a1a1" if self.current_theme == "light" else "#374151"
        )
        self.chat_scroll.pack(fill="both", expand=True, padx=20, pady=(10, 0))
        self.chat_scroll._parent_canvas.configure(highlightthickness=0)
        
        # Контейнер для сообщений внутри скролла
        self.chat_container = ctk.CTkFrame(
            self.chat_scroll,
            fg_color=self.colors["CHAT_BG"]
        )
        self.chat_container.pack(fill="both", expand=True)
        
        # Приветственное сообщение
        self.show_welcome_message()
        
        # ================= INPUT AREA =================
        self.input_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color=self.colors["CHAT_BG"],
            height=120
        )
        self.input_frame.pack(fill="x", padx=20, pady=10)
        
        # Поле ввода с кнопками
        input_container = ctk.CTkFrame(
            self.input_frame,
            fg_color=self.colors["AI_BUBBLE"],
            corner_radius=12,
            border_width=1,
            border_color=self.colors["BORDER_COLOR"]
        )
        input_container.pack(fill="x", pady=(0, 10))
        
        # Внутренний контейнер для кнопок и текстового поля
        inner_input_frame = ctk.CTkFrame(input_container, fg_color="transparent")
        inner_input_frame.pack(fill="both", expand=True, padx=15, pady=12)
        
        # Кнопка микрофона (слева)
        self.mic_btn = ctk.CTkButton(
            inner_input_frame,
            text="🎤",
            width=40,
            height=40,
            fg_color=self.colors["PRIMARY_COLOR"] if not self.voice_input_available else "transparent",
            hover_color=self.colors["PRIMARY_HOVER"] if not self.voice_input_available else self.colors["USER_BUBBLE"],
            text_color="white" if not self.voice_input_available else self.colors["TEXT_PRIMARY"],
            font=("Segoe UI", 14),
            corner_radius=20,
            command=self.toggle_voice_record
        )
        self.mic_btn.pack(side="left", padx=(0, 10))
        
        # Текстовое поле
        self.textbox = ctk.CTkTextbox(
            inner_input_frame,
            height=40,
            fg_color="transparent",
            text_color=self.colors["TEXT_PRIMARY"],
            wrap="word",
            font=("Segoe UI", 13),
            border_width=0
        )
        self.textbox.pack(side="left", fill="both", expand=True)
        self.setup_textbox_placeholder()
        
        # Кнопка отправки (справа)
        self.send_btn = ctk.CTkButton(
            inner_input_frame,
            text="➤",
            width=40,
            height=40,
            fg_color=self.colors["PRIMARY_COLOR"],
            hover_color=self.colors["PRIMARY_HOVER"],
            text_color="white",
            font=("Segoe UI", 14, "bold"),
            corner_radius=20,
            command=self.send_message
        )
        self.send_btn.pack(side="right")
        
        # Индикатор записи (скрыт по умолчанию)
        self.recording_indicator = ctk.CTkLabel(
            inner_input_frame,
            text="●",
            font=("Segoe UI", 16),
            text_color=self.colors["RECORDING_RED"],
            bg_color="transparent"
        )
        self.recording_indicator.pack(side="right", padx=(0, 10))
        self.recording_indicator.pack_forget()
        
        # Кнопки под полем ввода
        button_frame = ctk.CTkFrame(self.input_frame, fg_color="transparent")
        button_frame.pack(fill="x")
        
        # Левая часть - кнопка остановки голоса
        left_buttons = ctk.CTkFrame(button_frame, fg_color="transparent")
        left_buttons.pack(side="left")
        
        # Кнопка остановки голоса Jarvis
        self.stop_speech_btn = ctk.CTkButton(
            left_buttons,
            text="⏹️ Stop speaking",
            width=120,
            height=32,
            fg_color="#dc2626",
            hover_color="#b91c1c",
            text_color="white",
            font=("Segoe UI", 11),
            corner_radius=6,
            command=self.stop_jarvis_speech,
            state="disabled"  # Изначально отключена
        )
        self.stop_speech_btn.pack(side="left", padx=5)
        
        # Правая часть
        right_buttons = ctk.CTkFrame(button_frame, fg_color="transparent")
        right_buttons.pack(side="right")
        
        # Кнопка режима мышления
        self.think_btn = ctk.CTkButton(
            right_buttons,
            text="🤔 Enable reflections",
            width=140,
            height=32,
            fg_color="transparent",
            hover_color=self.colors["USER_BUBBLE"],
            text_color=self.colors["TEXT_SECONDARY"],
            font=("Segoe UI", 12),
            corner_radius=6,
            command=self.toggle_think
        )
        self.think_btn.pack(side="left", padx=5)
    
    def setup_textbox_placeholder(self):
        """Настроить плейсхолдер для текстового поля"""
        placeholder = "Write a message..."
        if not self.voice_input_available:
            placeholder = "Write a message... (🎤 - установите SpeechRecognition)"
        
        self.textbox.insert("1.0", placeholder)
        self.textbox.configure(text_color="#9ca3af")
        
        # Привязываем события
        self.textbox.bind("<FocusIn>", self.clear_placeholder_event)
        self.textbox.bind("<Key>", self.on_textbox_key)
        self.textbox.bind("<Return>", self.send_on_enter)
    
    def clear_placeholder_event(self, event=None):
        """Обработчик события очистки плейсхолдера"""
        self.clear_placeholder()
    
    def clear_placeholder(self):
        """Очистить плейсхолдер"""
        try:
            current_text = self.textbox.get("1.0", "end").strip()
            placeholder = "Напишите сообщение..."
            if not self.voice_input_available:
                placeholder = "Напишите сообщение... (🎤 - установите SpeechRecognition)"
            
            if current_text == placeholder:
                self.textbox.delete("1.0", "end")
                self.textbox.configure(text_color=self.colors["TEXT_PRIMARY"])
        except tk.TclError:
            pass  # Виджет уже уничтожен
    
    def on_textbox_key(self, event=None):
        """Обработка нажатия клавиш"""
        try:
            current_text = self.textbox.get("1.0", "end").strip()
            placeholder = "Напишите сообщение..."
            if not self.voice_input_available:
                placeholder = "Напишите сообщение... (🎤 - установите SpeechRecognition)"
            
            if current_text == placeholder:
                self.textbox.delete("1.0", "end")
                self.textbox.configure(text_color=self.colors["TEXT_PRIMARY"])
        except tk.TclError:
            pass
    
    def send_on_enter(self, event):
        """Отправить по Enter"""
        if not event.state & 0x1:  # Не нажат Shift
            self.send_message()
            return "break"
        return None
    
    def toggle_sidebar(self):
        """Переключить сайдбар"""
        if self.sidebar_visible:
            self.sidebar.pack_forget()
            self.sidebar_visible = False
            self.sidebar_toggle_btn.configure(text="☰")
        else:
            self.sidebar.pack(side="left", fill="y")
            self.sidebar_visible = True
            self.sidebar_toggle_btn.configure(text="✕")
    
    def toggle_voice_ui(self):
        """Переключить голос (воспроизведение)"""
        self.voice_enabled = not self.voice_enabled
        toggle_voice()
        self.voice_btn.configure(
            text="🔊" if self.voice_enabled else "🔇",
            fg_color=self.colors["PRIMARY_COLOR"] if not self.voice_enabled else "transparent",
            text_color="white" if not self.voice_enabled else self.colors["TEXT_PRIMARY"]
        )
    
    def stop_jarvis_speech(self):
        """Остановить речь Jarvis"""
        from voice import stop_speech
        stop_speech()
        self.is_jarvis_speaking = False
        self.stop_speech_btn.configure(state="disabled")
    
    def toggle_voice_record(self):
        """Переключить запись голоса (микрофон)"""
        if not self.voice_input_available:
            # Показываем сообщение с инструкцией по установке
            missing_deps = []
            if not self.voice_recognition_available:
                missing_deps.append("SpeechRecognition")
            if not self.sounddevice_available:
                missing_deps.append("sounddevice")
            if not self.scipy_available:
                missing_deps.append("scipy")
            
            deps_str = " ".join(missing_deps)
            messagebox.showinfo(
                "Установите зависимости", 
                f"Для голосового ввода установите:\n\npip install {deps_str}\n\n"
                "Или запустите в терминале:\n"
                "pip install SpeechRecognition sounddevice scipy\n\n"
                "После установки перезапустите приложение."
            )
            return
        
        if self.is_recording:
            self.stop_recording()
        else:
            self.start_recording()
    
    def start_recording(self):
        """Начать запись голоса"""
        self.is_recording = True
        
        # Меняем вид кнопки микрофона
        self.mic_btn.configure(
            text="⏹️",
            fg_color=self.colors["RECORDING_RED"],
            hover_color=self.colors["RECORDING_HOVER"],
            text_color="white"
        )
        
        # Показываем индикатор записи
        self.recording_indicator.pack(side="right", padx=(0, 10))
        
        # Запускаем анимацию индикатора
        self.animate_recording_indicator()
        
        # Запускаем запись в отдельном потоке
        threading.Thread(target=self.record_voice_thread, daemon=True).start()
    
    def animate_recording_indicator(self):
        """Анимировать индикатор записи"""
        if self.is_recording:
            current_color = self.recording_indicator.cget("text_color")
            new_color = "#ffffff" if current_color == self.colors["RECORDING_RED"] else self.colors["RECORDING_RED"]
            self.recording_indicator.configure(text_color=new_color)
            self.after(500, self.animate_recording_indicator)
    
    def record_voice_thread(self):
        """Поток для записи голоса"""
        try:
            # Запись аудио через sounddevice
            recording = sd.rec(
                int(self.recording_duration * self.fs),
                samplerate=self.fs,
                channels=1,
                dtype='int16'
            )
            sd.wait()
            
            # Сохраняем во временный файл
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as f:
                wav.write(f.name, self.fs, recording)
                
                # Распознаем речь
                with sr.AudioFile(f.name) as source:
                    audio = self.recognizer.record(source)
                    text = self.recognizer.recognize_google(audio, language="ru-RU")
                    
                    # Обновляем текстовое поле
                    self.after(0, self.set_voice_text, text)
                    
                # Удаляем временный файл
                os.unlink(f.name)
                
        except sr.UnknownValueError:
            self.after(0, self.show_voice_error, "Речь не распознана")
        except sr.RequestError as e:
            self.after(0, self.show_voice_error, f"Ошибка сервиса: {e}")
        except Exception as e:
            self.after(0, self.show_voice_error, f"Ошибка записи: {e}")
        finally:
            self.after(0, self.stop_recording)
    
    def stop_recording(self):
        """Остановить запись голоса"""
        self.is_recording = False
        
        # Возвращаем кнопку в исходное состояние
        self.mic_btn.configure(
            text="🎤",
            fg_color="transparent",
            hover_color=self.colors["USER_BUBBLE"],
            text_color=self.colors["TEXT_PRIMARY"]
        )
        
        # Скрываем индикатор записи
        self.recording_indicator.pack_forget()
    
    def set_voice_text(self, text):
        """Установить распознанный текст в поле ввода"""
        self.textbox.delete("1.0", "end")
        self.textbox.insert("1.0", text)
        self.textbox.configure(text_color=self.colors["TEXT_PRIMARY"])
        
        # Автоматически отправляем сообщение
        self.send_message()
    
    def show_voice_error(self, message):
        """Показать ошибку голосового ввода"""
        messagebox.showerror("Ошибка голосового ввода", message)
    
    def toggle_think(self):
        """Переключить режим мышления"""
        self.think_mode = not self.think_mode
        self.think_btn.configure(
            text="🤔 Размышления: ВКЛ" if self.think_mode else "🤔 Включить размышления",
            fg_color=self.colors["PRIMARY_COLOR"] if self.think_mode else "transparent",
            text_color="white" if self.think_mode else self.colors["TEXT_SECONDARY"]
        )
    
    def upload_file(self):
        """Загрузка файла"""
        try:
            file_path = filedialog.askopenfilename(
                title="Выберите файл",
                filetypes=[
                    ("Текстовые файлы", "*.txt *.md *.py *.js *.html *.css *.json"),
                    ("Все файлы", "*.*")
                ]
            )
            
            if file_path:
                print(f"Выбран файл: {file_path}")
                # Читаем содержимое файла
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Добавляем в чат
                filename = os.path.basename(file_path)
                message = f"📎 Файл: {filename}\n```\n{content[:1000]}{'...' if len(content) > 1000 else ''}\n```"
                self.add_user_message(message)
                self.current_chat.append({"role": "user", "content": f"Загружен файл: {filename}"})
                
        except Exception as e:
            print(f"Ошибка загрузки файла: {e}")
    
    # ================= THEME METHODS =================
    
    def toggle_theme(self):
        """Переключение темы"""
        if self.current_theme == "light":
            self.current_theme = "dark"
            ctk.set_appearance_mode("dark")
            self.colors = DARK_THEME
        else:
            self.current_theme = "light"
            ctk.set_appearance_mode("light")
            self.colors = LIGHT_THEME
        
        # Сохраняем тему
        if "settings" not in self.memory:
            self.memory["settings"] = {}
        self.memory["settings"]["theme"] = self.current_theme
        save_memory(self.memory)
        
        # Обновляем кнопку темы
        self.theme_btn.configure(
            text="☀️ Тема" if self.current_theme == "light" else "🌙 Тема",
            fg_color=self.colors["BACKGROUND"],
            hover_color=self.colors["USER_BUBBLE"],
            text_color=self.colors["TEXT_PRIMARY"]
        )
        
        # Перезагружаем интерфейс
        self.reload_interface()
    
    def reload_interface(self):
        """Перезагрузить интерфейс с новой темой"""
        # Сохраняем текущий чат
        current_chat_data = {
            "id": self.current_chat_id,
            "title": self.chat_title.cget("text"),
            "messages": self.current_chat.copy(),
            "think_mode": self.think_mode
        } if self.current_chat else None
        
        # Удаляем все виджеты
        for widget in self.winfo_children():
            widget.destroy()
        
        # Создаем интерфейс заново
        self.create_widgets()
        
        # Восстанавливаем чат если он был
        if current_chat_data and current_chat_data["messages"]:
            self.current_chat_id = current_chat_data["id"]
            self.current_chat = current_chat_data["messages"]
            self.think_mode = current_chat_data["think_mode"]
            
            self.chat_title.configure(text=current_chat_data["title"])
            self.think_btn.configure(
                text="🤔 Размышления: ВКЛ" if self.think_mode else "🤔 Включить размышления",
                fg_color=self.colors["PRIMARY_COLOR"] if self.think_mode else "transparent",
                text_color="white" if self.think_mode else self.colors["TEXT_SECONDARY"]
            )
            
            # Показываем сообщения
            self.show_chat_messages(self.current_chat)
        else:
            self.load_chat_history()
    
    # ================= CHAT METHODS =================
    
    def show_welcome_message(self):
        """Показать приветственное сообщение"""
        try:
            welcome_frame = ctk.CTkFrame(
                self.chat_container,
                fg_color="transparent",
                height=200
            )
            welcome_frame.pack(fill="x", pady=(50, 0))
            
            ctk.CTkLabel(
                welcome_frame,
                text="👋 Hello! I`m Jarvis",
                font=("Segoe UI", 28, "bold"),
                text_color=self.colors["TEXT_PRIMARY"]
            ).pack(pady=(0, 10))
            
            ctk.CTkLabel(
                welcome_frame,
                text="How can i help you!",
                font=("Segoe UI", 14),
                text_color=self.colors["TEXT_SECONDARY"]
            ).pack()
            
            if not self.voice_input_available:
                ctk.CTkLabel(
                    welcome_frame,
                    text="Для голосового ввода: pip install SpeechRecognition sounddevice scipy",
                    font=("Segoe UI", 11),
                    text_color="#ef4444"
                ).pack(pady=(10, 0))
            else:
                ctk.CTkLabel(
                    welcome_frame,
                    text="Click 🎤 for voice input",
                    font=("Segoe UI", 12),
                    text_color=self.colors["TEXT_SECONDARY"]
                ).pack(pady=(10, 0))
            
            # Прокручиваем к началу
            self.update_scroll_position()
            
        except tk.TclError:
            pass
    
    def add_user_message(self, text):
        """Добавить сообщение пользователя (справа)"""
        try:
            # Удаляем приветственное сообщение
            for widget in self.chat_container.winfo_children():
                try:
                    if widget.winfo_class() == "CTkFrame" and len(widget.winfo_children()) > 0:
                        first_child = widget.winfo_children()[0]
                        if first_child.winfo_class() == "CTkLabel":
                            child_text = first_child.cget("text")
                            if "👋 Привет! Я Jarvis" in child_text:
                                widget.destroy()
                                break
                except:
                    continue
            
            # Создаем контейнер для сообщения
            message_frame = ctk.CTkFrame(
                self.chat_container,
                fg_color="transparent"
            )
            message_frame.pack(fill="x", pady=(10, 5), padx=20)
            
            # Контейнер для выравнивания (справа)
            align_frame = ctk.CTkFrame(message_frame, fg_color="transparent")
            align_frame.pack(side="right", anchor="e")
            
            # Аватар пользователя
            avatar_frame = ctk.CTkFrame(align_frame, fg_color="transparent", width=40)
            avatar_frame.pack(side="right", padx=(10, 0))
            
            ctk.CTkLabel(
                avatar_frame,
                text="👤",
                font=("Segoe UI", 20),
                text_color=self.colors["TEXT_PRIMARY"],
                width=30,
                height=30
            ).pack()
            
            # Фрейм сообщения пользователя (правая сторона, синий цвет)
            text_frame = ctk.CTkFrame(
                align_frame, 
                fg_color=self.colors["USER_BUBBLE"],  # синий цвет для пользователя
                corner_radius=12,
                border_width=0
            )
            text_frame.pack(side="right")
            
            # Текст сообщения
            text_label = ctk.CTkLabel(
                text_frame,
                text=text,
                wraplength=500,
                justify="left",
                font=("Segoe UI", 13),
                text_color=self.colors["USER_TEXT"],  # белый текст на синем фоне
                padx=16,
                pady=12
            )
            text_label.pack(anchor="w")
            
            # Прокручиваем к новому сообщению
            self.update_scroll_position()
            
        except tk.TclError:
            pass
    
    def add_ai_message(self, text=""):
        """Добавить сообщение AI (слева)"""
        try:
            # Создаем контейнер для сообщения
            message_frame = ctk.CTkFrame(
                self.chat_container,
                fg_color="transparent"
            )
            message_frame.pack(fill="x", pady=(5, 10), padx=20)
            
            # Контейнер для выравнивания (слева)
            align_frame = ctk.CTkFrame(message_frame, fg_color="transparent")
            align_frame.pack(side="left", anchor="w")
            
            # Аватар Jarvis
            avatar_frame = ctk.CTkFrame(align_frame, fg_color="transparent", width=40)
            avatar_frame.pack(side="left", padx=(0, 10))
            
            ctk.CTkLabel(
                avatar_frame,
                text="🤖",
                font=("Segoe UI", 20),
                text_color=self.colors["TEXT_PRIMARY"],
                width=30,
                height=30
            ).pack()
            
            # Фрейм сообщения AI (левая сторона)
            text_frame = ctk.CTkFrame(
                align_frame, 
                fg_color=self.colors["AI_BUBBLE"],
                corner_radius=12,
                border_width=0
            )
            text_frame.pack(side="left")
            
            # Текст сообщения
            text_label = ctk.CTkLabel(
                text_frame,
                text=text,
                wraplength=500,
                justify="left",
                font=("Segoe UI", 13),
                text_color=self.colors["AI_TEXT"],
                padx=16,
                pady=12
            )
            text_label.pack(anchor="w")
            
            # Прокручиваем к новому сообщению
            self.update_scroll_position()
            
            return text_label
            
        except tk.TclError:
            return None
    
    def show_thinking_animation(self):
        """Показать анимацию мышления"""
        self.thinking_animation_active = True
        
        # Создаем контейнер для сообщения
        message_frame = ctk.CTkFrame(
            self.chat_container,
            fg_color="transparent"
        )
        message_frame.pack(fill="x", pady=(5, 10), padx=20)
        
        # Контейнер для выравнивания (слева)
        align_frame = ctk.CTkFrame(message_frame, fg_color="transparent")
        align_frame.pack(side="left", anchor="w")
        
        # Аватар Jarvis
        avatar_frame = ctk.CTkFrame(align_frame, fg_color="transparent", width=40)
        avatar_frame.pack(side="left", padx=(0, 10))
        
        ctk.CTkLabel(
            avatar_frame,
            text="🤖",
            font=("Segoe UI", 20),
            text_color=self.colors["TEXT_PRIMARY"],
            width=30,
            height=30
        ).pack()
        
        # Фрейм сообщения AI (левая сторона)
        text_frame = ctk.CTkFrame(
            align_frame, 
            fg_color=self.colors["AI_BUBBLE"],
            corner_radius=12,
            border_width=0
        )
        text_frame.pack(side="left")
        
        # Индикатор мышления
        thinking_label = ctk.CTkLabel(
            text_frame,
            text="Думаю",
            wraplength=500,
            justify="left",
            font=("Segoe UI", 13, "italic"),
            text_color=self.colors["AI_TEXT"],
            padx=16,
            pady=12
        )
        thinking_label.pack(anchor="w")
        
        # Запускаем анимацию
        self.animate_thinking(thinking_label)
        
        return thinking_label
    
    def animate_thinking(self, label, dots=0):
        """Анимировать индикатор мышления"""
        if self.thinking_animation_active:
            thinking_texts = ["Думаю", "Думаю.", "Думаю..", "Думаю..."]
            label.configure(text=thinking_texts[dots % 4])
            self.after(500, self.animate_thinking, label, dots + 1)
    
    def hide_thinking_animation(self):
        """Скрыть анимацию мышления"""
        self.thinking_animation_active = False
    
    def update_scroll_position(self):
        """Обновить позицию прокрутки"""
        try:
            # Ждем обновления виджетов
            self.update_idletasks()
            
            # Прокручиваем вниз
            self.chat_scroll._parent_canvas.yview_moveto(1.0)
            
            # Обновляем видимость скроллбара
            self.update_scrollbar_visibility()
            
        except:
            pass
    
    def update_scrollbar_visibility(self):
        """Обновить видимость скроллбара"""
        try:
            # Получаем размеры
            canvas = self.chat_scroll._parent_canvas
            scrollable_height = self.chat_container.winfo_height()
            visible_height = self.chat_scroll.winfo_height()
            
            # Если контент помещается в видимую область, скрываем скроллбар
            if scrollable_height <= visible_height:
                canvas.configure(yscrollcommand=None)
            else:
                # Показываем скроллбар
                scrollbar = self.chat_scroll._parent_canvas._scrollbar_y
                if scrollbar:
                    canvas.configure(yscrollcommand=scrollbar.set)
                    
        except:
            pass
    
    def show_chat_messages(self, messages):
        """Показать сообщения из истории"""
        for msg in messages:
            try:
                if msg["role"] == "user":
                    self.add_user_message(msg["content"])
                elif msg["role"] == "assistant":
                    self.add_ai_message(msg["content"])
            except:
                continue
        
        # Прокручиваем к последнему сообщению
        self.update_scroll_position()
    
    def send_message(self):
        """Отправить сообщение"""
        try:
            text = self.textbox.get("1.0", "end").strip()
            if not text or text == "Напишите сообщение..." or text == "Напишите сообщение... (🎤 - установите SpeechRecognition)":
                return
            
            self.textbox.delete("1.0", "end")
            
            # Добавляем сообщение пользователя (справа)
            self.add_user_message(text)
            self.current_chat.append({"role": "user", "content": text})
            
            # Показываем анимацию мышления если включен режим
            thinking_label = None
            if self.think_mode:
                thinking_label = self.show_thinking_animation()
            
            # Показываем индикатор загрузки (слева)
            ai_label = self.add_ai_message("▌")
            
            # Отправляем запрос
            threading.Thread(
                target=self.get_ai_response,
                args=(text, ai_label, thinking_label),
                daemon=True
            ).start()
            
        except Exception as e:
            print(f"Ошибка отправки сообщения: {e}")
    
    def get_ai_response(self, text, ai_label, thinking_label):
        """Получить ответ от AI"""
        system_prompt = f"You are Jarvis — smart, charismatic. Style: short, clear.\nThink: {self.think_mode}"
        
        payload = {
            "model": MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
            ],
            "stream": True
        }
        
        full_reply = ""
        
        try:
            with requests.post(OLLAMA_URL, json=payload, stream=True, timeout=30) as r:
                r.raise_for_status()
                for line in r.iter_lines():
                    if line:
                        try:
                            data = json.loads(line.decode())
                            if "message" in data and "content" in data["message"]:
                                full_reply += data["message"]["content"]
                        except:
                            continue
                            
        except requests.exceptions.ConnectionError:
            full_reply = "❌ Ошибка подключения к Ollama\nУбедитесь, что Ollama запущен: `ollama serve`"
        except requests.exceptions.Timeout:
            full_reply = "⏱️ Время ожидания истекло\nПопробуйте еще раз"
        except Exception as e:
            full_reply = f"⚠️ Ошибка: {str(e)}"
        
        full_reply = parse_markdown(full_reply)
        
        # Скрываем анимацию мышления
        self.hide_thinking_animation()
        if thinking_label and thinking_label.winfo_exists():
            thinking_label.master.master.destroy()  # Удаляем фрейм с анимацией
        
        # Анимируем вывод
        if ai_label:
            try:
                self.after(0, self.animate_response, ai_label, full_reply)
            except:
                pass
    
    def animate_response(self, ai_label, text):
        """Анимировать вывод ответа"""
        try:
            if not ai_label or not ai_label.winfo_exists():
                return
            
            ai_label.configure(text="")
            self.is_jarvis_speaking = True
            self.stop_speech_btn.configure(state="normal")  # Включаем кнопку остановки
            
            def type_writer(idx=0):
                try:
                    if idx < len(text) and ai_label.winfo_exists():
                        current = ai_label.cget("text")
                        ai_label.configure(text=current + text[idx])
                        self.after(10, type_writer, idx + 1)
                        # Прокручиваем если есть скролл
                        self.update_scroll_position()
                    else:
                        # Сохраняем ответ
                        self.current_chat.append({"role": "assistant", "content": text})
                        
                        # Озвучиваем если включено
                        if self.voice_enabled:
                            # Запускаем речь в отдельном потоке
                            def speak_thread():
                                speak(text)
                                self.after(0, lambda: self.stop_speech_btn.configure(state="disabled"))
                                self.is_jarvis_speaking = False
                            
                            threading.Thread(target=speak_thread, daemon=True).start()
                        else:
                            self.stop_speech_btn.configure(state="disabled")
                            self.is_jarvis_speaking = False
                        
                        # Сохраняем чат
                        self.save_chat()
                except:
                    pass
            
            type_writer()
            
        except tk.TclError:
            pass
    
    # ================= HISTORY METHODS =================
    
    def load_chat_history(self):
        """Загрузить историю чатов"""
        try:
            for widget in self.chat_list_scroll.winfo_children():
                widget.destroy()
            
            chats = self.memory.get("chats", {})
            
            if not chats:
                ctk.CTkLabel(
                    self.chat_list_scroll,
                    text="Нет сохраненных чатов",
                    font=("Segoe UI", 11),
                    text_color=self.colors["TEXT_SECONDARY"]
                ).pack(pady=20)
                return
            
            # Показываем последние 10 чатов
            sorted_chats = sorted(
                chats.items(),
                key=lambda x: x[1].get("timestamp", ""),
                reverse=True
            )[:10]
            
            for chat_id, chat_data in sorted_chats:
                title = chat_data.get("title", "Беседа")
                
                btn = ctk.CTkButton(
                    self.chat_list_scroll,
                    text=f"💬 {title[:25]}{'...' if len(title) > 25 else ''}",
                    width=200,
                    height=36,
                    fg_color="transparent",
                    hover_color="#e5e5e5" if self.current_theme == "light" else "#374151",
                    text_color=self.colors["TEXT_PRIMARY"],
                    font=("Segoe UI", 11),
                    anchor="w",
                    corner_radius=6,
                    command=lambda cid=chat_id: self.load_chat(cid)
                )
                btn.pack(fill="x", pady=2)
                
        except tk.TclError:
            pass
    
    def save_chat(self):
        """Сохранить текущий чат"""
        try:
            if not self.current_chat:
                return
            
            if not self.current_chat_id:
                self.current_chat_id = str(uuid.uuid4())[:8]
            
            # Создаем заголовок
            first_msg = next((msg["content"] for msg in self.current_chat if msg["role"] == "user"), "Беседа")
            title = first_msg[:40] + "..." if len(first_msg) > 40 else first_msg
            
            # Сохраняем
            if "chats" not in self.memory:
                self.memory["chats"] = {}
                
            self.memory["chats"][self.current_chat_id] = {
                "id": self.current_chat_id,
                "title": title,
                "timestamp": datetime.datetime.now().isoformat(),
                "messages": self.current_chat.copy(),
                "think_mode": self.think_mode
            }
            
            save_memory(self.memory)
            self.chat_title.configure(text=title)
            self.load_chat_history()
            
        except Exception as e:
            print(f"Ошибка сохранения чата: {e}")
    
    def load_chat(self, chat_id):
        """Загрузить чат"""
        try:
            if chat_id not in self.memory.get("chats", {}):
                return
            
            chat_data = self.memory["chats"][chat_id]
            
            # Устанавливаем текущий чат
            self.current_chat_id = chat_id
            self.current_chat = chat_data.get("messages", [])
            self.think_mode = chat_data.get("think_mode", False)
            
            # Обновляем UI
            self.chat_title.configure(text=chat_data.get("title", "Чат"))
            self.think_btn.configure(
                text="🤔 Размышления: ВКЛ" if self.think_mode else "🤔 Включить размышления",
                fg_color=self.colors["PRIMARY_COLOR"] if self.think_mode else "transparent",
                text_color="white" if self.think_mode else self.colors["TEXT_SECONDARY"]
            )
            
            # Очищаем контейнер чата
            for widget in self.chat_container.winfo_children():
                try:
                    widget.destroy()
                except:
                    pass
            
            # Показываем сообщения
            self.show_chat_messages(self.current_chat)
            
        except Exception as e:
            print(f"Ошибка загрузки чата: {e}")
    
    def new_chat(self):
        """Новая беседа"""
        try:
            # Сохраняем текущий чат
            if self.current_chat:
                self.save_chat()
            
            # Сбрасываем
            self.current_chat = []
            self.current_chat_id = None
            self.think_mode = False
            
            # Обновляем UI
            self.chat_title.configure(text="Новая беседа")
            self.think_btn.configure(
                text="🤔 Включить размышления",
                fg_color="transparent",
                text_color=self.colors["TEXT_SECONDARY"]
            )
            
            # Очищаем контейнер чата
            for widget in self.chat_container.winfo_children():
                try:
                    widget.destroy()
                except:
                    pass
            
            self.show_welcome_message()
            
        except Exception as e:
            print(f"Ошибка создания нового чата: {e}")
    
    def clear_all_history(self):
        """Очистить всю историю"""
        try:
            if not self.memory.get("chats"):
                return
            
            if messagebox.askyesno("Очистка истории", "Удалить всю историю чатов?"):
                self.memory["chats"] = {}
                save_memory(self.memory)
                self.load_chat_history()
                self.new_chat()
                
        except Exception as e:
            print(f"Ошибка очистки истории: {e}")
    
    def on_closing(self):
        """Обработка закрытия"""
        print("Закрытие приложения...")
        try:
            if self.current_chat:
                self.save_chat()
            self.quit()
            self.destroy()
        except:
            self.destroy()


if __name__ == "__main__":
    print("🚀 Запуск Jarvis AI Assistant...")
    print("="*50)
    if not VOICE_INPUT_AVAILABLE:
        print("⚠️ Голосовой ввод недоступен")
        print("Установите: pip install SpeechRecognition sounddevice scipy")
    print("="*50)
    try:
        app = JarvisApp()
        app.mainloop()
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")