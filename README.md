# J.A.R.V.I.S 🤖  
**AI-powered desktop assistant built with Python**

J.A.R.V.I.S (Just A Rather Very Intelligent System) is a desktop AI assistant designed to interact with the user through voice commands, process natural language locally using LLMs, and execute system-level actions.  
The project focuses on clean architecture, modularity, and practical AI integration rather than simple demos.

This project was developed as a long-term portfolio project to demonstrate skills in **Python development, AI integration, and software architecture**.

---

## ✨ Key Features
- 🎙️ Voice recognition and speech-to-text input  
- 🧠 Local Large Language Model (LLM) integration via Ollama  
- 🖥️ Desktop graphical user interface  
- ⚙️ Execution of system-level commands  
- 🧩 Modular and scalable architecture  
- 🔒 No cloud dependency for core AI logic  

---

## 🧠 Architecture Overview
The project follows a modular design where each responsibility is clearly separated:

- **Core logic** is isolated from UI  
- **Voice processing** is independent from AI reasoning  
- **Utilities** are reusable and extendable  

This allows:
- Easy replacement of AI models  
- Future plugin support  
- Better maintainability and testing  

---

## 📁 Project Structure
J.A.R.V.I.S/
│
├── core/ # Core AI logic and processing
│ ├── brain.py
│ └── command_router.py
│
├── utils/ # Helper utilities
│ ├── config.py
│ └── logger.py
│
├── gui.py # Desktop GUI
├── assistant.py # Assistant controller
├── voice_manager.py # Voice recognition and audio handling
├── jarvis.py # Application entry point
│
├── requirements.txt
├── README.md
└── .gitignore

---

## 🛠️ Tech Stack
- **Language:** Python  
- **Voice Recognition:** SpeechRecognition  
- **AI / LLM:** Ollama (local models)  
- **GUI:** Tkinter / CustomTkinter  
- **Platform:** Windows (planned cross-platform support)

---

## ▶️ Installation & Run

### 1️⃣ Clone the repository
```bash
git clone https://github.com/LazizYT/Jarvis.git
cd Jarvis
```

🎯 Project Goals
The main goals of J.A.R.V.I.S are:
Build a realistic AI assistant, not a toy project
Work with local AI models instead of cloud APIs
Practice clean code and architecture
Create a strong portfolio project for CS / AI applications

🚧 Current Status
Core assistant logic implemented
Voice input working
Local LLM connected
GUI functional

The project is under active development.

🔮 Future Improvements
🔌 Plugin-based command system
🧠 Improved intent recognition
🧑‍💻 VS Code and system tool integration
🌍 Cross-platform support (Linux / macOS)
🗣️ Text-to-speech output

⚠️ Notes
The project intentionally avoids hardcoded API keys
Sensitive configuration is expected to be stored in .env files
Virtual environments (.venv) are excluded from version control

👤 Author
Laziz
High school student from Uzbekistan
Aspiring Computer Science & Artificial Intelligence student

This project represents my interest in AI systems, automation, and real-world software engineering.

⭐ Acknowledgements
Open-source Python community
Ollama for enabling local LLM usage
SpeechRecognition contributors

📜 License
This project is released for educational and portfolio purposes.
