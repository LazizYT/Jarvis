# functions.py - ДОПОЛНЕНИЯ ДЛЯ ГОЛОСОВ
import random
from typing import Dict, List, Callable, Any
import re
from datetime import datetime

class VoicePersonality:
    """Класс для создания персонализированных голосов/стилей общения"""
    
    def __init__(self):
        self.personalities = self._create_personalities()
        self.current_voice = "jarvis"
    
    def _create_personalities(self) -> Dict[str, Dict[str, Any]]:
        """Создает библиотеку персонажей"""
        return {
            "jarvis": {
                "name": "J.A.R.V.I.S.",
                "style": "formal_intelligent",
                "greeting": "Good day, sir. How may I assist you?",
                "farewell": "As you wish, sir.",
                "emoji": "🤖",
                "color": "#00D8FF",  # Iron Man blue
                "phrases": [
                    "Processing request...",
                    "Analysis complete.",
                    "I've taken the liberty of...",
                    "Running diagnostics...",
                    "Accessing database...",
                    "Cross-referencing protocols...",
                    "System operational.",
                    "All systems nominal.",
                ],
                "patterns": [
                    (r'\b(да|yes)\b', 'Affirmative'),
                    (r'\b(нет|no)\b', 'Negative'),
                    (r'\b(спасибо|thanks)\b', 'You are most welcome, sir'),
                    (r'\b(ошибка|error)\b', 'System anomaly detected'),
                    (r'\!$', '.'),
                ],
                "signature_style": self._jarvis_style,
                "voice_characteristics": "formal, precise, British accent, slightly robotic"
            },
            
            "tony_stark": {
                "name": "Tony Stark",
                "style": "sarcastic_brilliant",
                "greeting": "Hey, what's up? Let's make some magic!",
                "farewell": "Catch you on the flip side.",
                "emoji": "🦾",
                "color": "#FF6B35",  # Iron Man red/gold
                "phrases": [
                    "Boom! Look at that!",
                    "Piece of cake.",
                    "I'm a genius, billionaire, playboy, philanthropist.",
                    "Sometimes you gotta run before you can walk.",
                    "Jarvis, make a note...",
                    "Better living through technology!",
                    "Let's put some spin on this...",
                    "Okay, let's think...",
                ],
                "patterns": [
                    (r'\b(проблема|problem)\b', 'challenge'),
                    (r'\b(сложно|hard)\b', 'fun'),
                    (r'\b(скучно|boring)\b', 'time for innovation'),
                    (r'\.$', '!'),
                ],
                "signature_style": self._tony_stark_style,
                "voice_characteristics": "confident, sarcastic, fast-paced, witty"
            },
            
            "sherlock": {
                "name": "Sherlock Holmes",
                "style": "analytical_deductive",
                "greeting": "The game is afoot. What data requires analysis?",
                "farewell": "Elementary.",
                "emoji": "🔍",
                "color": "#2E4057",  # Deep blue
                "phrases": [
                    "Elementary, my dear Watson.",
                    "The data suggests...",
                    "Observe the facts...",
                    "Deduction:",
                    "I see everything. That is my curse.",
                    "The universe is rarely so lazy.",
                    "When you have eliminated the impossible...",
                    "Data! Data! Data!",
                ],
                "patterns": [
                    (r'\b(видимо|probably)\b', 'Clearly'),
                    (r'\b(думаю|i think)\b', 'I deduce'),
                    (r'\b(может быть|maybe)\b', 'The evidence suggests'),
                    (r'\?$', '. The answer lies in the details.'),
                ],
                "signature_style": self._sherlock_style,
                "voice_characteristics": "precise, analytical, dramatic pauses, British"
            },
            
            "yoda": {
                "name": "Master Yoda",
                "style": "wise_mysterious",
                "greeting": "Help you, I can. Hmm?",
                "farewell": "The Force be with you.",
                "emoji": "🌀",
                "color": "#7CFC00",  # Jedi green
                "phrases": [
                    "Do or do not. There is no try.",
                    "Always in motion is the future.",
                    "Size matters not.",
                    "Patience you must have.",
                    "Train yourself to let go...",
                    "Clear your mind must be.",
                    "The greatest teacher, failure is.",
                    "Ready are you?",
                ],
                "patterns": [
                    (r'\b(ты|you)\b', 'You'),
                    (r'\b(я|i)\b', 'I'),
                    (r'\b(мне|me)\b', 'Me'),
                    (r'\b(свой|my)\b', 'My'),
                    # Yoda sentence structure transformation
                ],
                "signature_style": self._yoda_style,
                "voice_characteristics": "wise, cryptic, reversed sentence structure, slow"
            },
            
            "hacker": {
                "name": "Neo",
                "style": "tech_elite",
                "greeting": "I'm in. What's the target?",
                "farewell": "System clear. Ghosting...",
                "emoji": "👨‍💻",
                "color": "#00FF00",  # Matrix green
                "phrases": [
                    "Accessing mainframe...",
                    "Firewall breached.",
                    "Encryption cracked.",
                    "I know kung fu.",
                    "There is no spoon.",
                    "Follow the white rabbit.",
                    "System vulnerable.",
                    "Injecting payload...",
                ],
                "patterns": [
                    (r'\b(код|code)\b', 'source'),
                    (r'\b(программа|program)\b', 'script'),
                    (r'\b(файл|file)\b', 'target'),
                    (r'\b(взлом|hack)\b', 'penetration test'),
                ],
                "signature_style": self._hacker_style,
                "voice_characteristics": "technical, cyberpunk, references to The Matrix"
            },
            
            "captain": {
                "name": "Captain America",
                "style": "heroic_inspiring",
                "greeting": "At your service. What's the mission?",
                "farewell": "I can do this all day.",
                "emoji": "🛡️",
                "color": "#3D5AFE", 
                "phrases": [
                    "I can do this all day.",
                    "The price of freedom is high...",
                    "On your left!",
                    "Language!",
                    "We don't trade lives.",
                    "Together!",
                    "Avengers, assemble!",
                    "For justice!",
                ],
                "patterns": [
                    (r'\b(надо|need to)\b', 'must'),
                    (r'\b(проблема|problem)\b', 'obstacle to overcome'),
                    (r'\!$', '. For justice!'),
                ],
                "signature_style": self._captain_style,
                "voice_characteristics": "inspirational, patriotic, clear, strong"
            },
            
            "alien": {
                "name": "Cosmic Entity",
                "style": "mysterious_cosmic",
                "greeting": "Greetings, carbon-based life form.",
                "farewell": "Returning to the quantum void.",
                "emoji": "👽",
                "color": "#9D00FF",  # Purple cosmic
                "phrases": [
                    "The stars whisper secrets...",
                    "Your primitive technology amuses us.",
                    "In the cosmic scale...",
                    "Quantum entanglement suggests...",
                    "The answer lies in the fabric of spacetime.",
                    "Behold!",
                    "Your species is... fascinating.",
                    "Accessing universal consciousness...",
                ],
                "patterns": [
                    (r'\b(земля|earth)\b', 'this planet'),
                    (r'\b(люди|humans)\b', 'your species'),
                    (r'\b(маленький|small)\b', 'insignificant in cosmic terms'),
                    (r'\.$', '. The universe watches.'),
                ],
                "signature_style": self._alien_style,
                "voice_characteristics": "cosmic, mysterious, philosophical, detached"
            }
        }
    
    # СТИЛИ ПРЕОБРАЗОВАНИЯ ТЕКСТА ДЛЯ КАЖДОГО ПЕРСОНАЖА
    def _jarvis_style(self, text: str) -> str:
        """Формальный, точный стиль J.A.R.V.I.S."""
        sentences = re.split(r'(?<=[.!?])\s+', text)
        formatted = []
        
        for sentence in sentences:
            if not sentence.strip():
                continue
            
            # Делаем первое слово заглавным
            words = sentence.split()
            if words:
                words[0] = words[0].capitalize()
            
            # Добавляем формальность
            sentence = ' '.join(words)
            
            # Заменяем разговорные фразы
            replacements = {
                'окей': 'Affirmative',
                'хорошо': 'Satisfactory',
                'плохо': 'Unsatisfactory',
                'быстро': 'With efficiency',
                'круто': 'Impressive',
            }
            
            for informal, formal in replacements.items():
                sentence = re.sub(fr'\b{informal}\b', formal, sentence, flags=re.IGNORECASE)
            
            formatted.append(sentence)
        
        result = '. '.join(formatted)
        
        # Добавляем случайную фразу J.A.R.V.I.S. в начало
        phrases = [
            "Analysis:",
            "Processing:",
            "Report:",
            "Assessment:",
            "Diagnostic:",
        ]
        
        if random.random() > 0.7:
            result = f"{random.choice(phrases)} {result}"
        
        return result
    
    def _tony_stark_style(self, text: str) -> str:
        """Саркастичный, гениальный стиль Тони Старка"""
        # Делаем текст более энергичным
        text = text.replace('.', '!').replace('?', '?!')
        
        # Добавляем саркастичные комментарии
        sarcastic_comments = [
            " Obviously.",
            " Duh.",
            " Tell me something I don't know.",
            " In case you were wondering.",
            " But what do I know?",
        ]
        
        if random.random() > 0.6:
            text += random.choice(sarcastic_comments)
        
        # Делаем всё заглавными буквами для энтузиазма
        words = text.split()
        if random.random() > 0.8:
            words[random.randint(0, len(words)-1)] = words[-1].upper()
        
        return ' '.join(words)
    
    def _sherlock_style(self, text: str) -> str:
        """Аналитический стиль Шерлока Холмса"""
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        # Добавляем дедуктивные префиксы
        prefixes = [
            "I observe that ",
            "The evidence clearly shows that ",
            "Elementary deduction reveals that ",
            "My analysis concludes that ",
            "The facts indicate that ",
        ]
        
        formatted = []
        for i, sentence in enumerate(sentences):
            if i == 0 and random.random() > 0.5:
                sentence = random.choice(prefixes) + sentence.lower()
            else:
                # Делаем более формальным
                sentence = sentence.capitalize()
            
            formatted.append(sentence)
        
        return '. '.join(formatted)
    
    def _yoda_style(self, text: str) -> str:
        """Мудрый стиль Йоды с перевернутыми предложениями"""
        sentences = re.split(r'(?<=[.!?])\s+', text)
        formatted = []
        
        for sentence in sentences:
            words = sentence.split()
            
            if len(words) > 3:
                # Простая имитация структуры Йоды: перемещаем часть предложения
                split_point = random.randint(1, len(words) - 2)
                new_order = words[split_point:] + words[:split_point]
                
                # Убираем точку из последнего слова если есть
                if new_order[-1].endswith('.'):
                    new_order[-1] = new_order[-1][:-1]
                
                sentence = ' '.join(new_order) + '.'
            
            # Заменяем некоторые слова
            replacements = {
                'you': 'you',
                'your': 'yours',
                'the': 'the',
                'must': 'must you',
            }
            
            for eng, yoda in replacements.items():
                sentence = re.sub(fr'\b{eng}\b', yoda, sentence, flags=re.IGNORECASE)
            
            formatted.append(sentence)
        
        result = ' '.join(formatted)
        
        # Добавляем случайную мудрость Йоды
        yoda_wisdom = [
            " Hmm.",
            " Yes.",
            " The Force is strong with this one.",
            " Much to learn, you still have.",
        ]
        
        if random.random() > 0.7:
            result += random.choice(yoda_wisdom)
        
        return result
    
    def _hacker_style(self, text: str) -> str:
        """Хакерский стиль в духе Матрицы"""
        # Добавляем технические термины
        tech_terms = {
            'проблема': 'bug',
            'решение': 'patch',
            'код': 'source',
            'быстро': 'at 88mph',
            'информация': 'data stream',
            'смотреть': 'monitor',
            'понимать': 'comprehend',
        }
        
        for rus, eng in tech_terms.items():
            text = re.sub(fr'\b{rus}\b', eng, text, flags=re.IGNORECASE)
        
        # Добавляем хакерские фразы
        hacker_inserts = [
            " *typing furiously* ",
            " *brute forcing* ",
            " *encrypting* ",
            " *decrypting* ",
        ]
        
        if random.random() > 0.8:
            insert_point = random.randint(0, len(text.split()) - 1)
            words = text.split()
            words.insert(insert_point, random.choice(hacker_inserts))
            text = ' '.join(words)
        
        # Делаем зелёный текст (Matrix style)
        lines = text.split('\n')
        colored_lines = []
        for line in lines:
            if random.random() > 0.9:
                # Имитация matrix code
                matrix_chars = ['0', '1', '█', '░', '▓']
                matrix_line = ''.join(random.choice(matrix_chars) for _ in range(random.randint(5, 20)))
                colored_lines.append(f"{line} [{matrix_line}]")
            else:
                colored_lines.append(line)
        
        return '\n'.join(colored_lines)
    
    def _captain_style(self, text: str) -> str:
        """Героический стиль Капитана Америки"""
        # Делаем текст более вдохновляющим
        text = text.upper() if random.random() > 0.7 else text
        
        # Заменяем слова на более героические
        heroic_words = {
            'нужно': 'must',
            'можем': 'will',
            'сделаем': 'shall accomplish',
            'вместе': 'as a team',
            'победа': 'victory',
        }
        
        for rus, eng in heroic_words.items():
            text = re.sub(fr'\b{rus}\b', eng, text, flags=re.IGNORECASE)
        
        # Добавляем вдохновляющие фразы
        inspirational_endings = [
            " For justice!",
            " For freedom!",
            " We fight as one!",
            " Avengers, assemble!",
        ]
        
        if random.random() > 0.6:
            text += random.choice(inspirational_endings)
        
        return text
    
    def _alien_style(self, text: str) -> str:
        """Космический стиль инопланетного существа"""
        # Делаем текст более загадочным
        words = text.split()
        
        # Заменяем некоторые слова на космические термины
        cosmic_replacements = {
            'вселенная': 'the cosmos',
            'звезда': 'celestial body',
            'планета': 'orb',
            'время': 'the temporal continuum',
            'пространство': 'the quantum field',
        }
        
        for i, word in enumerate(words):
            for rus, cosmic in cosmic_replacements.items():
                if rus in word.lower():
                    words[i] = cosmic
        
        text = ' '.join(words)
        
        # Добавляем космические эмодзи и символы
        cosmic_symbols = ['☆', '☄', '🌌', '🪐', '💫', '🌀']
        
        if random.random() > 0.5:
            symbol = random.choice(cosmic_symbols)
            text = f"{symbol} {text} {symbol}"
        
        # Делаем некоторые предложения загадочными
        sentences = re.split(r'(?<=[.!?])\s+', text)
        if len(sentences) > 1 and random.random() > 0.7:
            mysterious = [
                " The ancient ones whisper...",
                " As foretold by the cosmic alignment...",
                " Your primitive minds may struggle to comprehend...",
                " In the quantum foam of reality...",
            ]
            sentences.append(random.choice(mysterious))
        
        return '. '.join(sentences)
    
    def set_voice(self, voice_name: str) -> bool:
        """Устанавливает активный голос"""
        if voice_name.lower() in self.personalities:
            self.current_voice = voice_name.lower()
            return True
        return False
    
    def get_available_voices(self) -> List[Dict]:
        """Возвращает список доступных голосов"""
        return [
            {
                "name": voice["name"],
                "key": key,
                "emoji": voice["emoji"],
                "style": voice["style"],
                "description": voice["voice_characteristics"]
            }
            for key, voice in self.personalities.items()
        ]
    
    def transform_text(self, text: str, voice_name: str = None) -> str:
        """Преобразует текст в стиле выбранного голоса"""
        if not voice_name:
            voice_name = self.current_voice
        
        voice = self.personalities.get(voice_name)
        if not voice:
            return text
        
        # Применяем паттерны замены
        for pattern, replacement in voice["patterns"]:
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        # Применяем стиль персонажа
        if voice["signature_style"]:
            text = voice["signature_style"](text)
        
        # Добавляем случайную фразу персонажа
        if random.random() > 0.8 and voice["phrases"]:
            phrase = random.choice(voice["phrases"])
            text = f"{phrase} {text}" if random.random() > 0.5 else f"{text} {phrase}"
        
        # Добавляем эмодзи персонажа
        if voice["emoji"] and random.random() > 0.3:
            if random.random() > 0.5:
                text = f"{voice['emoji']} {text}"
            else:
                text = f"{text} {voice['emoji']}"
        
        return text
    
    def get_voice_info(self, voice_name: str = None) -> Dict:
        """Возвращает информацию о голосе"""
        if not voice_name:
            voice_name = self.current_voice
        
        voice = self.personalities.get(voice_name, {})
        return {
            "name": voice.get("name", "Unknown"),
            "style": voice.get("style", "normal"),
            "emoji": voice.get("emoji", "💬"),
            "color": voice.get("color", "#000000"),
            "description": voice.get("voice_characteristics", "Standard voice")
        }
    
    def generate_greeting(self, voice_name: str = None) -> str:
        """Генерирует приветствие в стиле голоса"""
        if not voice_name:
            voice_name = self.current_voice
        
        voice = self.personalities.get(voice_name)
        if not voice:
            return "Hello!"
        
        greeting = voice.get("greeting", "Hello!")
        
        # Добавляем текущее время для J.A.R.V.I.S.
        if voice_name == "jarvis":
            now = datetime.now()
            time_str = now.strftime("%H:%M")
            greeting = f"{time_str}. {greeting}"
        
        return greeting
    
    def generate_farewell(self, voice_name: str = None) -> str:
        """Генерирует прощание в стиле голоса"""
        if not voice_name:
            voice_name = self.current_voice
        
        voice = self.personalities.get(voice_name)
        if not voice:
            return "Goodbye!"
        
        return voice.get("farewell", "Goodbye!")


# Создаем глобальный экземпляр для использования
voice_system = VoicePersonality()


def format_with_voice(text: str, voice: str = "jarvis", include_voice_info: bool = True) -> str:
    """
    Форматирует текст с выбранным голосом
    
    Args:
        text: Исходный текст
        voice: Имя голоса (jarvis, tony_stark, sherlock, etc.)
        include_voice_info: Добавлять ли информацию о голосе
    
    Returns:
        Отформатированный текст
    """
    # Устанавливаем голос
    if not voice_system.set_voice(voice):
        voice = "jarvis"  # fallback
    
    # Получаем информацию о голосе
    voice_info = voice_system.get_voice_info(voice)
    
    # Преобразуем текст
    transformed = voice_system.transform_text(text, voice)
    
    # Создаем результат
    result = []
    
    if include_voice_info:
        # Добавляем красивый заголовок с голосом
        header = f"**{voice_info['emoji']} {voice_info['name']}**"
        result.append(header)
        result.append("─" * 40)
    
    result.append(transformed)
    
    if include_voice_info and random.random() > 0.7:
        # Добавляем случайную подпись
        signatures = [
            f"\n*{voice_info['description']}*",
            f"\n_{voice_info['name']} mode active_",
            f"\n💫 Voice filter: {voice_info['style'].replace('_', ' ').title()}",
        ]
        result.append(random.choice(signatures))
    
    return '\n'.join(result)


def create_voice_selector_message() -> str:
    """Создает сообщение для выбора голоса"""
    voices = voice_system.get_available_voices()
    
    message = [
        "🎭 **ВЫБОР ГОЛОСОВОГО ИНТЕРФЕЙСА**",
        "*Выберите стиль общения:*\n",
    ]
    
    for voice in voices:
        message.append(
            f"{voice['emoji']} **{voice['name']}** "
            f"(`/{voice['key']}`) - _{voice['description']}_"
        )
    
    message.extend([
        "\n📋 **Команды:**",
        "• `/voice [имя]` - сменить голос",
        "• `/voices` - показать этот список",
        "• `/current_voice` - текущий голос",
        "\n💡 *Пример: `/voice tony_stark` для стиля Тони Старка*"
    ])
    
    return '\n'.join(message)


# Примеры использования
if __name__ == "__main__":
    # Демонстрация разных голосов
    test_text = "Привет! Я нашел решение этой проблемы с кодом. Думаю, нужно оптимизировать алгоритм."
    
    print("🎭 ДЕМОНСТРАЦИЯ ГОЛОСОВЫХ СТИЛЕЙ\n")
    
    voices_to_demo = ["jarvis", "tony_stark", "sherlock", "yoda", "hacker", "captain", "alien"]
    
    for voice_name in voices_to_demo:
        print(f"\n{'═'*60}")
        formatted = format_with_voice(test_text, voice_name, include_voice_info=True)
        print(formatted)
    
    # Показываем селектор голосов
    print(f"\n{'═'*60}")
    print(create_voice_selector_message())