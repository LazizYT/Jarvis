# core/ollama_client.py
"""
Клиент для работы с Ollama API
"""

import json
import requests
from typing import Dict, List, Any, Optional, Generator
from markdown_parser import parse_markdown

class OllamaClient:
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3"):
        """
        Инициализация клиента Ollama
        
        Args:
            base_url: URL сервера Ollama
            model: Название модели
        """
        self.base_url = base_url
        self.model = model
        self.chat_url = f"{base_url}/api/chat"
        self.generate_url = f"{base_url}/api/generate"

    def _messages_to_prompt(self, messages: List[Dict[str, str]]) -> str:
        parts = []
        for msg in messages:
            role = msg.get("role", "")
            content = msg.get("content", "")
            if role == "system":
                parts.append(f"System: {content}")
            elif role == "user":
                parts.append(f"User: {content}")
            elif role == "assistant":
                parts.append(f"Assistant: {content}")
            else:
                parts.append(content)
        parts.append("Assistant:")
        return "\n".join(parts)
    
    def generate_response(self, messages: List[Dict[str, str]], 
                         think_mode: bool = False, 
                         stream: bool = True) -> Generator[str, None, None]:
        """
        Сгенерировать ответ от модели
        
        Args:
            messages: История сообщений
            think_mode: Режим размышлений
            stream: Потоковый режим
            
        Yields:
            Части ответа
        """
        system_prompt = f"You are Jarvis — smart, charismatic. Style: short, clear.\nThink: {think_mode}"
        
        # Добавляем системное сообщение если его нет
        if not any(msg.get("role") == "system" for msg in messages):
            messages.insert(0, {"role": "system", "content": system_prompt})
        
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": stream,
            "options": {
                "temperature": 0.7,
                "top_p": 0.9,
                "top_k": 40
            }
        }
        
        try:
            response = requests.post(self.chat_url, json=payload, stream=True, timeout=60)
            response.raise_for_status()
            
            for line in response.iter_lines():
                if not line:
                    continue
                
                try:
                    data = json.loads(line.decode())
                    if "message" in data and "content" in data["message"]:
                        yield data["message"]["content"]
                except json.JSONDecodeError:
                    continue
                    
        except requests.exceptions.ConnectionError:
            yield "❌ Ошибка подключения к Ollama\nУбедитесь, что Ollama запущен: `ollama serve`"
        except requests.exceptions.Timeout:
            yield "⏱️ Время ожидания истекло\nПопробуйте еще раз"
        except Exception as e:
            yield f"⚠️ Ошибка: {str(e)}"
    
    def generate_complete_response(self, messages: List[Dict[str, str]], 
                                  think_mode: bool = False) -> str:
        """
        Сгенерировать полный ответ (без потокового режима)
        
        Returns:
            Полный ответ
        """
        full_response = ""
        for chunk in self.generate_response(messages, think_mode, stream=True):
            full_response += chunk
        
        return parse_markdown(full_response)
    
    def test_connection(self) -> bool:
        """Проверить соединение с Ollama"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def get_available_models(self) -> List[str]:
        """Получить список доступных моделей"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return [model["name"] for model in data.get("models", [])]
        except:
            pass
        return []
    
    def pull_model(self, model_name: str) -> Generator[str, None, None]:
        """Загрузить модель"""
        try:
            response = requests.post(
                f"{self.base_url}/api/pull",
                json={"name": model_name},
                stream=True,
                timeout=300
            )
            response.raise_for_status()
            
            for line in response.iter_lines():
                if not line:
                    continue
                
                try:
                    data = json.loads(line.decode())
                    if "status" in data:
                        yield data["status"]
                except:
                    continue
                    
        except Exception as e:
            yield f"Ошибка загрузки модели: {str(e)}"
