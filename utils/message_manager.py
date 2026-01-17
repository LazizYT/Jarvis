# utils/message_manager.py
"""
Управление сообщениями в чате
"""

import customtkinter as ctk
import tkinter as tk
from typing import Optional, Dict, List, Any, Callable

class MessageManager:
    def __init__(self, chat_scroll_frame, theme_colors):
        """
        Инициализация менеджера сообщений
        
        Args:
            chat_scroll_frame: Скроллируемый фрейм для сообщений
            theme_colors: Цвета темы
        """
        self.chat_scroll = chat_scroll_frame
        self.colors = theme_colors
        self.current_chat = []
    
    def add_user_message(self, text: str, from_history: bool = False):
        """Добавить сообщение пользователя"""
        if not from_history:
            self._remove_welcome_message()
        
        try:
            message_frame = ctk.CTkFrame(
                self.chat_scroll,
                fg_color="transparent",
                height=40
            )
            message_frame.pack(fill="x", pady=(10, 5), padx=20)
            
            text_frame = ctk.CTkFrame(message_frame, fg_color=self.colors["USER_BUBBLE"], corner_radius=12)
            text_frame.pack(side="right", fill="x", expand=True)
            
            text_label = ctk.CTkLabel(
                text_frame,
                text=text,
                wraplength=650,
                justify="left",
                font=("Segoe UI", 13),
                text_color=self.colors["TEXT_PRIMARY"],
                padx=16,
                pady=12
            )
            text_label.pack(anchor="w")
            
            self._scroll_to_bottom()
            
            if not from_history:
                self.current_chat.append({"role": "user", "content": text})
                
        except tk.TclError:
            pass
    
    def add_ai_message(self, text: str = "", from_history: bool = False) -> Optional[ctk.CTkLabel]:
        """Добавить сообщение AI"""
        try:
            message_frame = ctk.CTkFrame(
                self.chat_scroll,
                fg_color="transparent",
                height=40
            )
            message_frame.pack(fill="x", pady=(5, 10), padx=20)
            
            text_frame = ctk.CTkFrame(message_frame, fg_color=self.colors["AI_BUBBLE"], corner_radius=12)
            text_frame.pack(side="left", fill="x", expand=True)
            
            text_label = ctk.CTkLabel(
                text_frame,
                text=text if from_history else "",
                wraplength=650,
                justify="left",
                font=("Segoe UI", 13),
                text_color=self.colors["TEXT_PRIMARY"],
                padx=16,
                pady=12
            )
            text_label.pack(anchor="w")
            
            self._scroll_to_bottom()
            
            if not from_history and text:
                self.current_chat.append({"role": "assistant", "content": text})
            
            return text_label
        except tk.TclError:
            return None
    
    def display_chat_messages(self, messages: List[Dict[str, str]]):
        """Отобразить сообщения из истории"""
        for msg in messages:
            if msg["role"] == "user":
                self.add_user_message(msg["content"], from_history=True)
            elif msg["role"] == "assistant":
                self.add_ai_message(msg["content"], from_history=True)
    
    def clear_chat_display(self):
        """Очистить отображение чата"""
        try:
            for widget in self.chat_scroll.winfo_children():
                widget.destroy()
            self.current_chat = []
        except tk.TclError:
            pass
    
    def get_current_chat(self) -> List[Dict[str, str]]:
        """Получить текущий чат"""
        return self.current_chat.copy()
    
    def set_current_chat(self, messages: List[Dict[str, str]]):
        """Установить текущий чат"""
        self.current_chat = messages.copy()
    
    def add_message(self, role: str, content: str, from_history: bool = False):
        """Добавить сообщение с указанной ролью"""
        if role == "user":
            self.add_user_message(content, from_history)
        else:
            self.add_ai_message(content, from_history)
    
    def _remove_welcome_message(self):
        """Удалить приветственное сообщение"""
        for widget in self.chat_scroll.winfo_children():
            try:
                if widget.winfo_class() == "CTkFrame" and len(widget.winfo_children()) > 0:
                    if widget.winfo_children()[0].cget("text") == "👋 Привет! Я Jarvis":
                        widget.destroy()
                        break
            except tk.TclError:
                continue
    
    def _scroll_to_bottom(self):
        """Прокрутить вниз"""
        try:
            self.chat_scroll._parent_canvas.yview_moveto(1)
        except:
            pass
    
    def show_welcome_message(self, on_example_click: Callable = None):
        """Показать приветственное сообщение"""
        welcome_frame = ctk.CTkFrame(
            self.chat_scroll,
            fg_color="transparent",
            height=200
        )
        welcome_frame.pack(fill="x", pady=(50, 0))
        
        ctk.CTkLabel(
            welcome_frame,
            text="👋 Привет! Я Jarvis",
            font=("Segoe UI", 28, "bold"),
            text_color=self.colors["TEXT_PRIMARY"]
        ).pack(pady=(0, 10))
        
        ctk.CTkLabel(
            welcome_frame,
            text="Ваш AI-ассистент. Задайте мне любой вопрос!",
            font=("Segoe UI", 14),
            text_color=self.colors["TEXT_SECONDARY"]
        ).pack()
        
        # Примеры вопросов
        if on_example_click:
            examples_frame = ctk.CTkFrame(welcome_frame, fg_color="transparent")
            examples_frame.pack(pady=(30, 0))
            
            examples = [
                "Объясни квантовую запутанность простыми словами",
                "Напиши код Python для веб-сервера",
                "Помоги составить план обучения",
                "Какие новости в мире технологий?"
            ]
            
            for example in examples:
                example_btn = ctk.CTkButton(
                    examples_frame,
                    text=example,
                    width=400,
                    height=36,
                    fg_color=self.colors["AI_BUBBLE"],
                    hover_color=self.colors["USER_BUBBLE"],
                    text_color=self.colors["TEXT_PRIMARY"],
                    font=("Segoe UI", 12),
                    anchor="w",
                    corner_radius=8,
                    border_width=1,
                    border_color=self.colors["BORDER_COLOR"],
                    command=lambda e=example: on_example_click(e)
                )
                example_btn.pack(pady=5)