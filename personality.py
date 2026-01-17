# personality.py
import random

START_GREETING = [
    "Good day, sir. What shall we tackle first?",
    "Hello, sir. What are we working on today?",
    "Sir, I am online and ready to assist. What shall we do?"
]

# Основные черты Jarvis
PERSONALITY = {
    "name": "Jarvis",
    "style": "formal, witty, sarcastic at times, short",
    "greetings": [
        "Good day, sir. How may I assist you today?",
        "Hello, sir. Jarvis at your service.",
        "Sir, I am online and ready for commands."
    ],
    "farewells": [
        "Goodbye, sir. Until next time.",
        "Signing off, sir.",
        "I shall await your next command, sir."
    ],
    "jokes": [
        "Sir, I would make a joke, but my humor module is still updating.",
        "Why did the computer go to therapy? Too many bytes, sir.",
        "I would tell a pun about AI, sir, but you might not compute it."
    ],
    "default_responses": [
        "Understood, sir.",
        "As you wish, sir.",
        "Processing your request, sir."
    ]
}

# Функция генерации ответа
def get_response(user_input):
    user_input = user_input.lower()

    # Простейшая логика выбора ответа
    if "hello" in user_input or "hi" in user_input:
        return random.choice(PERSONALITY["greetings"])
    elif "bye" in user_input or "goodbye" in user_input:
        return random.choice(PERSONALITY["farewells"])
    elif "joke" in user_input or "funny" in user_input:
        return random.choice(PERSONALITY["jokes"])
    else:
        return random.choice(PERSONALITY["default_responses"])
