# memory.py
import json
import os
import datetime

MEMORY_FILE = "memory.json"

def load_memory():
    """Загружаем память из файла"""
    if not os.path.exists(MEMORY_FILE):
        # Создаем структуру по умолчанию
        default_memory = {
            "chats": {},  # История чатов
            "settings": {
                "voice_enabled": True,
                "think_mode": False,
                "theme": "light",
                "auto_save": True,
                "max_history": 50
            },
            "user_preferences": {},
            "statistics": {
                "total_chats": 0,
                "total_messages": 0,
                "last_active": None
            }
        }
        save_memory(default_memory)
        return default_memory
    
    try:
        with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
            # Миграция старых форматов
            if "history" in data and "chats" not in data:
                # Конвертируем старый формат в новый
                data["chats"] = {}
                for i, chat in enumerate(data.get("history", [])):
                    chat_id = f"chat_{i}_{datetime.datetime.now().strftime('%Y%m%d')}"
                    first_message = next((msg["content"] for msg in chat if msg["role"] == "user"), "")
                    title = first_message[:40] + "..." if len(first_message) > 40 else first_message
                    
                    data["chats"][chat_id] = {
                        "id": chat_id,
                        "title": title if title else "Беседа",
                        "timestamp": datetime.datetime.now().isoformat(),
                        "messages": chat,
                        "think_mode": False
                    }
                
                # Обновляем статистику
                data["statistics"] = {
                    "total_chats": len(data["chats"]),
                    "total_messages": sum(len(chat["messages"]) for chat in data["chats"].values()),
                    "last_active": datetime.datetime.now().isoformat()
                }
                
                # Удаляем старый ключ
                if "history" in data:
                    del data["history"]
                    
                # Сохраняем мигрированные данные
                save_memory(data)
            
            return data
    except Exception as e:
        print(f"Ошибка загрузки памяти: {e}")
        # Возвращаем память по умолчанию в случае ошибки
        return {
            "chats": {},
            "settings": {
                "voice_enabled": True,
                "think_mode": False,
                "theme": "light",
                "auto_save": True,
                "max_history": 50
            },
            "user_preferences": {},
            "statistics": {
                "total_chats": 0,
                "total_messages": 0,
                "last_active": None
            }
        }

def save_memory(memory_data):
    """Сохраняем память в файл"""
    try:
        # Обновляем статистику
        memory_data["statistics"]["total_chats"] = len(memory_data.get("chats", {}))
        memory_data["statistics"]["total_messages"] = sum(
            len(chat.get("messages", [])) for chat in memory_data.get("chats", {}).values()
        )
        memory_data["statistics"]["last_active"] = datetime.datetime.now().isoformat()
        
        # Ограничиваем историю (удаляем старые чаты, если превышен лимит)
        max_history = memory_data.get("settings", {}).get("max_history", 50)
        chats = memory_data.get("chats", {})
        
        if len(chats) > max_history:
            # Сортируем по дате и оставляем только последние max_history
            sorted_chats = sorted(
                chats.items(),
                key=lambda x: x[1].get("timestamp", ""),
                reverse=True
            )[:max_history]
            
            memory_data["chats"] = dict(sorted_chats)
        
        # Сохраняем в файл
        with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(memory_data, f, ensure_ascii=False, indent=2)
        
        return True
    except Exception as e:
        print(f"Ошибка сохранения памяти: {e}")
        return False

def add_chat(memory_data, chat_id, chat_title, messages, think_mode=False):
    """Добавляем новый чат в память"""
    if "chats" not in memory_data:
        memory_data["chats"] = {}
    
    memory_data["chats"][chat_id] = {
        "id": chat_id,
        "title": chat_title,
        "timestamp": datetime.datetime.now().isoformat(),
        "messages": messages.copy() if messages else [],
        "think_mode": think_mode
    }
    
    return save_memory(memory_data)

def update_chat(memory_data, chat_id, messages=None, title=None, think_mode=None):
    """Обновляем существующий чат"""
    if chat_id not in memory_data.get("chats", {}):
        return False
    
    chat = memory_data["chats"][chat_id]
    
    if messages is not None:
        chat["messages"] = messages.copy()
    
    if title is not None:
        chat["title"] = title
    
    if think_mode is not None:
        chat["think_mode"] = think_mode
    
    chat["timestamp"] = datetime.datetime.now().isoformat()  # Обновляем время
    
    return save_memory(memory_data)

def delete_chat(memory_data, chat_id):
    """Удаляем чат из памяти"""
    if chat_id in memory_data.get("chats", {}):
        del memory_data["chats"][chat_id]
        return save_memory(memory_data)
    return False

def get_chat(memory_data, chat_id):
    """Получаем чат по ID"""
    return memory_data.get("chats", {}).get(chat_id)

def get_recent_chats(memory_data, limit=10):
    """Получаем последние чаты"""
    chats = memory_data.get("chats", {})
    
    # Сортируем по дате (новые первыми)
    sorted_chats = sorted(
        chats.items(),
        key=lambda x: x[1].get("timestamp", ""),
        reverse=True
    )[:limit]
    
    return {chat_id: chat_data for chat_id, chat_data in sorted_chats}

def search_chats(memory_data, query):
    """Ищем чаты по тексту"""
    results = {}
    query_lower = query.lower()
    
    for chat_id, chat_data in memory_data.get("chats", {}).items():
        # Ищем в заголовке
        if query_lower in chat_data.get("title", "").lower():
            results[chat_id] = chat_data
            continue
        
        # Ищем в сообщениях
        for message in chat_data.get("messages", []):
            if query_lower in message.get("content", "").lower():
                results[chat_id] = chat_data
                break
    
    return results

def get_statistics(memory_data):
    """Получаем статистику"""
    stats = memory_data.get("statistics", {})
    
    # Рассчитываем среднее количество сообщений в чате
    total_chats = stats.get("total_chats", 0)
    total_messages = stats.get("total_messages", 0)
    
    avg_messages = total_messages / total_chats if total_chats > 0 else 0
    
    return {
        **stats,
        "avg_messages_per_chat": round(avg_messages, 1),
        "active_chats": len(memory_data.get("chats", {}))
    }

def export_memory(export_path="memory_backup.json"):
    """Экспортируем всю память в файл"""
    memory_data = load_memory()
    
    try:
        with open(export_path, 'w', encoding='utf-8') as f:
            json.dump(memory_data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Ошибка экспорта: {e}")
        return False

def import_memory(import_path):
    """Импортируем память из файла"""
    try:
        with open(import_path, 'r', encoding='utf-8') as f:
            imported_data = json.load(f)
        
        # Объединяем с существующей памятью
        current_memory = load_memory()
        
        # Объединяем чаты
        for chat_id, chat_data in imported_data.get("chats", {}).items():
            if chat_id not in current_memory["chats"]:
                current_memory["chats"][chat_id] = chat_data
            else:
                # Если чат уже существует, обновляем его
                current_memory["chats"][chat_id].update(chat_data)
        
        # Сохраняем объединенные данные
        save_memory(current_memory)
        return True
    except Exception as e:
        print(f"Ошибка импорта: {e}")
        return False

def clear_all_memory():
    """Очищаем всю память"""
    try:
        os.remove(MEMORY_FILE)
        return True
    except Exception as e:
        print(f"Ошибка очистки памяти: {e}")
        return False