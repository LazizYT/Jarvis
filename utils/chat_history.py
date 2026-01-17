# utils/chat_history.py
"""
Управление историей чатов
"""

import datetime
import uuid
import customtkinter as ctk
import tkinter as tk
from typing import Dict, List, Any, Optional
from memory import load_memory, save_memory

class ChatHistoryManager:
    def __init__(self, sidebar_frame, chat_list_frame, chat_title_label, theme_colors):
        """
        Инициализация менеджера истории
        
        Args:
            sidebar_frame: Фрейм сайдбара
            chat_list_frame: Фрейм списка чатов
            chat_title_label: Label заголовка чата
            theme_colors: Цвета темы
        """
        self.sidebar_frame = sidebar_frame
        self.chat_list_frame = chat_list_frame
        self.chat_title_label = chat_title_label
        self.colors = theme_colors
        
        self.memory = load_memory()
        self.chat_buttons = {}
        self.active_chat_frame = None
        
        if "chats" not in self.memory:
            self.memory["chats"] = {}
    
    def load_chat_history(self):
        """Загрузить историю чатов в сайдбар"""
        # Очищаем текущий список
        for widget in self.chat_list_frame.winfo_children():
            widget.destroy()
        
        # Получаем список чатов
        chats = self.memory.get("chats", {})
        
        if not chats:
            # Показываем сообщение, если нет истории
            empty_label = ctk.CTkLabel(
                self.chat_list_frame,
                text="Нет сохраненных чатов",
                font=("Segoe UI", 11),
                text_color=self.colors["TEXT_SECONDARY"]
            )
            empty_label.pack(pady=20)
            return
        
        # Сортируем чаты по дате (новые сверху)
        sorted_chats = sorted(
            chats.items(),
            key=lambda x: x[1].get("timestamp", ""),
            reverse=True
        )
        
        # Ограничиваем количество отображаемых чатов
        for chat_id, chat_data in sorted_chats[:15]:
            self._add_chat_to_sidebar(chat_id, chat_data)
    
    def _add_chat_to_sidebar(self, chat_id: str, chat_data: Dict[str, Any]):
        """Добавить чат в сайдбар"""
        title = chat_data.get("title", "Беседа")
        timestamp = chat_data.get("timestamp", "")
        message_count = len(chat_data.get("messages", []))
        
        # Форматируем время
        time_str = self._format_timestamp(timestamp)
        
        # Создаем фрейм для кнопки чата
        chat_btn_frame = ctk.CTkFrame(self.chat_list_frame, fg_color="transparent", height=44)
        chat_btn_frame.pack(fill="x", pady=1)
        
        # Основная кнопка чата
        chat_btn = ctk.CTkButton(
            chat_btn_frame,
            text=f"💬 {title[:25]}{'...' if len(title) > 25 else ''}",
            width=200,
            height=36,
            fg_color="transparent",
            hover_color="#e5e5e5" if self.colors.get("theme", "light") == "light" else "#374151",
            text_color=self.colors["TEXT_PRIMARY"],
            font=("Segoe UI", 11),
            anchor="w",
            corner_radius=6,
            command=lambda cid=chat_id: self.load_saved_chat(cid)
        )
        chat_btn.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        # Кнопка удаления
        delete_btn = ctk.CTkButton(
            chat_btn_frame,
            text="✕",
            width=28,
            height=28,
            fg_color="transparent",
            hover_color="#fee2e2" if self.colors.get("theme", "light") == "light" else "#7f1d1d",
            text_color=self.colors["TEXT_SECONDARY"],
            font=("Segoe UI", 10),
            command=lambda cid=chat_id: self.delete_chat(cid)
        )
        delete_btn.pack(side="right")
        
        # Информация под кнопкой
        info_frame = ctk.CTkFrame(chat_btn_frame, fg_color="transparent")
        info_frame.pack(fill="x", padx=(10, 0))
        
        ctk.CTkLabel(
            info_frame,
            text=f"{time_str} • {message_count} сообщ.",
            font=("Segoe UI", 9),
            text_color=self.colors["TEXT_SECONDARY"]
        ).pack(anchor="w")
        
        # Сохраняем ссылку на кнопку
        self.chat_buttons[chat_id] = chat_btn_frame
    
    def _format_timestamp(self, timestamp: str) -> str:
        """Форматировать временную метку"""
        if not timestamp:
            return ""
        
        try:
            dt = datetime.datetime.fromisoformat(timestamp)
            return dt.strftime("%d.%m %H:%M")
        except:
            return timestamp[:10]
    
    def generate_chat_id(self) -> str:
        """Сгенерировать уникальный ID для чата"""
        return str(uuid.uuid4())
    
    def generate_chat_title(self, first_message: str) -> str:
        """Сгенерировать заголовок чата"""
        if len(first_message) > 40:
            return first_message[:40] + "..."
        return first_message
    
    def save_current_chat(self, chat_id: Optional[str], messages: List[Dict], 
                         think_mode: bool, title: Optional[str] = None) -> str:
        """
        Сохранить текущий чат
        
        Returns:
            ID сохраненного чата
        """
        if not messages:
            raise ValueError("Нет сообщений для сохранения")
        
        # Если у чата еще нет ID, создаем новый
        if not chat_id:
            chat_id = self.generate_chat_id()
        
        # Генерируем заголовок
        if not title:
            first_user_msg = next(
                (msg["content"] for msg in messages if msg["role"] == "user"),
                "Беседа"
            )
            title = self.generate_chat_title(first_user_msg)
        
        # Сохраняем чат
        self.memory["chats"][chat_id] = {
            "id": chat_id,
            "title": title,
            "timestamp": datetime.datetime.now().isoformat(),
            "messages": messages.copy(),
            "think_mode": think_mode
        }
        
        # Сохраняем в файл
        save_memory(self.memory)
        
        return chat_id
    
    def load_saved_chat(self, chat_id: str) -> Optional[Dict[str, Any]]:
        """Загрузить сохраненный чат"""
        if chat_id not in self.memory["chats"]:
            return None
        
        chat_data = self.memory["chats"][chat_id]
        
        # Обновляем заголовок
        self.chat_title_label.configure(text=chat_data.get("title", "Загруженный чат"))
        
        # Подсвечиваем активный чат
        self._highlight_active_chat(chat_id)
        
        return chat_data
    
    def _highlight_active_chat(self, chat_id: str):
        """Подсветить активный чат в сайдбаре"""
        # Сбрасываем подсветку у всех чатов
        for cid, frame in self.chat_buttons.items():
            try:
                if frame.winfo_exists():
                    if cid == chat_id:
                        frame.configure(fg_color="#10a37f")  # Просто зеленый
                        self.active_chat_frame = frame
                    else:
                        frame.configure(fg_color="transparent")
            except tk.TclError:
                continue
    
    def delete_chat(self, chat_id: str) -> bool:
        """Удалить чат из истории"""
        if chat_id in self.memory["chats"]:
            # Удаляем из памяти
            del self.memory["chats"][chat_id]
            
            # Сохраняем изменения
            save_memory(self.memory)
            
            # Обновляем сайдбар
            self.load_chat_history()
            
            return True
        return False
    
    def clear_all_history(self) -> bool:
        """Очистить всю историю"""
        if not self.memory["chats"]:
            return False
        
        self.memory["chats"] = {}
        save_memory(self.memory)
        
        # Обновляем UI
        self.chat_buttons.clear()
        self.load_chat_history()
        
        return True
    
    def get_chat_count(self) -> int:
        """Получить количество сохраненных чатов"""
        return len(self.memory.get("chats", {}))
    
    def search_chats(self, query: str) -> List[Dict[str, Any]]:
        """Поиск чатов по тексту"""
        results = []
        query_lower = query.lower()
        
        for chat_id, chat_data in self.memory.get("chats", {}).items():
            # Ищем в заголовке
            if query_lower in chat_data.get("title", "").lower():
                results.append(chat_data)
                continue
            
            # Ищем в сообщениях
            for message in chat_data.get("messages", []):
                if query_lower in message.get("content", "").lower():
                    results.append(chat_data)
                    break
        
        return results