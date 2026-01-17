# utils/theme_manager.py
"""
Управление темой приложения
"""

import customtkinter as ctk
from typing import Dict, Any

class ThemeManager:
    def __init__(self):
        self.current_theme = "light"
        self.colors = self.get_light_theme()
    
    def get_light_theme(self) -> Dict[str, str]:
        """Получить светлую цветовую схему"""
        return {
            "theme": "light",
            "PRIMARY_COLOR": "#10a37f",
            "PRIMARY_HOVER": "#0d8c6d",
            "BACKGROUND": "#ffffff",
            "SIDEBAR_BG": "#f7f7f8",
            "CHAT_BG": "#ffffff",
            "USER_BUBBLE": "#f2f2f2",
            "AI_BUBBLE": "#f7f7f8",
            "TEXT_PRIMARY": "#374151",
            "TEXT_SECONDARY": "#6b7280",
            "BORDER_COLOR": "#e5e7eb",
            "ACCENT_BLUE": "#3b82f6"
        }
    
    def get_dark_theme(self) -> Dict[str, str]:
        """Получить темную цветовую схему"""
        return {
            "theme": "dark",
            "PRIMARY_COLOR": "#10a37f",
            "PRIMARY_HOVER": "#0d8c6d",
            "BACKGROUND": "#171717",
            "SIDEBAR_BG": "#1f1f1f",
            "CHAT_BG": "#171717",
            "USER_BUBBLE": "#2a2a2a",
            "AI_BUBBLE": "#262626",
            "TEXT_PRIMARY": "#f3f4f6",
            "TEXT_SECONDARY": "#9ca3af",
            "BORDER_COLOR": "#374151",
            "ACCENT_BLUE": "#3b82f6"
        }
    
    def set_theme(self, theme: str):
        """Установить тему"""
        if theme == "dark":
            self.current_theme = "dark"
            self.colors = self.get_dark_theme()
            ctk.set_appearance_mode("dark")
        else:
            self.current_theme = "light"
            self.colors = self.get_light_theme()
            ctk.set_appearance_mode("light")
    
    def toggle_theme(self) -> str:
        """Переключить тему"""
        if self.current_theme == "light":
            self.set_theme("dark")
        else:
            self.set_theme("light")
        return self.current_theme
    
    def get_current_theme(self) -> str:
        """Получить текущую тему"""
        return self.current_theme
    
    def get_colors(self) -> Dict[str, str]:
        """Получить текущие цвета"""
        return self.colors
    
    def update_widget_color(self, widget, property_name: str, color_key: str):
        """Обновить цвет виджета"""
        color = self.colors.get(color_key)
        if color and hasattr(widget, 'configure'):
            try:
                widget.configure(**{property_name: color})
            except:
                pass