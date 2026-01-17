# voice_commands.py
from functions import voice_system, format_with_voice, create_voice_selector_message
import re

class VoiceCommandHandler:
    def __init__(self):
        self.user_voices = {}  # user_id -> voice_name
        
    def handle_command(self, user_id: str, command: str, text: str = "") -> str:
        """
        Обрабатывает голосовые команды
        
        Args:
            user_id: ID пользователя
            command: Команда (/voice, /voices, etc.)
            text: Текст для преобразования
        
        Returns:
            Ответное сообщение
        """
        command = command.lower().strip()
        
        if command in ["/voices", "/голоса", "/стили"]:
            return create_voice_selector_message()
            
        elif command in ["/current_voice", "/текущий", "/голос"]:
            voice_name = self.user_voices.get(user_id, "jarvis")
            voice_info = voice_system.get_voice_info(voice_name)
            return (
                f"🎭 **Текущий голос:** {voice_info['emoji']} {voice_info['name']}\n"
                f"📝 **Стиль:** {voice_info['style'].replace('_', ' ').title()}\n"
                f"💬 **Описание:** {voice_info['description']}\n\n"
                f"💡 Используйте `/voices` для выбора другого голоса"
            )
            
        elif command.startswith("/voice ") or command.startswith("/голос "):
            # Извлекаем имя голоса из команды
            parts = command.split()
            if len(parts) < 2:
                return "❓ Укажите имя голоса. Например: `/voice tony_stark`"
            
            voice_name = parts[1].lower()
            
            # Проверяем существование голоса
            if not voice_system.set_voice(voice_name):
                available = voice_system.get_available_voices()
                voice_list = "\n".join([f"• `{v['key']}` - {v['emoji']} {v['name']}" 
                                      for v in available])
                return (
                    f"❌ Голос `{voice_name}` не найден.\n\n"
                    f"📋 Доступные голоса:\n{voice_list}\n\n"
                    f"💡 Используйте `/voices` для подробного списка"
                )
            
            # Сохраняем выбор пользователя
            self.user_voices[user_id] = voice_name
            voice_info = voice_system.get_voice_info(voice_name)
            
            greeting = voice_system.generate_greeting(voice_name)
            
            return (
                f"✅ Голос изменен!\n\n"
                f"{voice_info['emoji']} **{voice_info['name']}** активирован.\n"
                f"💬 *{voice_info['voice_characteristics']}*\n\n"
                f"{greeting}"
            )
        
        elif command in ["/jarvis", "/джарвис"]:
            self.user_voices[user_id] = "jarvis"
            return format_with_voice("Голос J.A.R.V.I.S. активирован.", "jarvis")
            
        elif command in ["/tony", "/stark", "/тони", "/старк"]:
            self.user_voices[user_id] = "tony_stark"
            return format_with_voice("Режим Тони Старка активирован. Давайте творить!", "tony_stark")
            
        elif command in ["/sherlock", "/шерлок"]:
            self.user_voices[user_id] = "sherlock"
            return format_with_voice("Элементарно. Режим дедукции активирован.", "sherlock")
            
        elif command in ["/yoda", "/йода"]:
            self.user_voices[user_id] = "yoda"
            return format_with_voice("Активирован, мой голос. Мудрость дать, я могу.", "yoda")
            
        elif command in ["/hacker", "/neo", "/хакер", "/нео"]:
            self.user_voices[user_id] = "hacker"
            return format_with_voice("*typing* Система взломана. Хакерский режим активен.", "hacker")
            
        elif command in ["/captain", "/america", "/капитан"]:
            self.user_voices[user_id] = "captain"
            return format_with_voice("Я могу делать это весь день. Героический режим активирован!", "captain")
            
        elif command in ["/alien", "/инопланетянин"]:
            self.user_voices[user_id] = "alien"
            return format_with_voice("👽 Приветствую, землянин. Космический режим активирован.", "alien")
            
        elif command in ["/reset_voice", "/сброс"]:
            self.user_voices[user_id] = "jarvis"
            return "🔄 Голос сброшен до стандартного J.A.R.V.I.S."
        
        return "❓ Неизвестная команда. Используйте `/voices` для списка доступных команд."
    
    def process_message(self, user_id: str, message: str) -> str:
        """
        Обрабатывает обычное сообщение с учетом выбранного голоса
        """
        # Проверяем, есть ли команда
        if message.startswith('/'):
            return None  # Команды обрабатываются отдельно
        
        # Получаем голос пользователя
        voice_name = self.user_voices.get(user_id, "jarvis")
        
        # Преобразуем сообщение в стиле выбранного голоса
        return format_with_voice(message, voice_name, include_voice_info=False)


# Пример интеграции с ботом
def create_bot_response(user_id: str, user_message: str) -> str:
    """
    Пример функции для интеграции с ботом
    """
    handler = VoiceCommandHandler()
    
    # Проверяем, является ли сообщение командой
    if user_message.startswith('/'):
        return handler.handle_command(user_id, user_message)
    
    # Обрабатываем обычное сообщение
    transformed_user_msg = handler.process_message(user_id, user_message)
    
    # Здесь была бы генерация ответа AI
    # Для примера, просто возвращаем преобразованное сообщение
    ai_response = f"Вы сказали: {user_message}"
    
    # Преобразуем ответ AI в стиле пользователя
    voice_name = handler.user_voices.get(user_id, "jarvis")
    final_response = format_with_voice(ai_response, voice_name)
    
    return final_response


# Демонстрация
if __name__ == "__main__":
    print("🤖 ДЕМОНСТРАЦИЯ СИСТЕМЫ ГОЛОСОВ\n")
    
    handler = VoiceCommandHandler()
    
    # Пользователь выбирает голос
    print("👤 Пользователь: /voice tony_stark")
    print(handler.handle_command("user123", "/voice tony_stark"))
    print()
    
    print("👤 Пользователь: Привет, как дела?")
    response = create_bot_response("user123", "Привет, как дела?")
    print(f"🤖 Бот: {response}")
    print()
    
    print("👤 Пользователь: /voice yoda")
    print(handler.handle_command("user123", "/voice yoda"))
    print()
    
    print("👤 Пользователь: Есть проблема с кодом")
    response = create_bot_response("user123", "Есть проблема с кодом")
    print(f"🤖 Бот: {response}")