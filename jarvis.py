# jarvis.py (основной файл запуска)
import sys
import signal
import threading
from gui import JarvisApp

def signal_handler(sig, frame):
    """Обработчик сигнала прерывания"""
    print("\n👋 Завершение работы Jarvis...")
    sys.exit(0)

def main():
    """Основная функция запуска приложения"""
    # Устанавливаем обработчик сигналов
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        # Запускаем приложение
        app = JarvisApp()
        
        # Настраиваем обработку закрытия окна
        def on_closing():
            print("Закрытие приложения...")
            app.quit()
            app.destroy()
            sys.exit(0)
        
        app.protocol("WM_DELETE_WINDOW", on_closing)
        
        # Запускаем главный цикл
        print("🚀 Запуск Jarvis AI Assistant...")
        app.mainloop()
        
    except KeyboardInterrupt:
        print("\n👋 Прервано пользователем")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Ошибка при запуске: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()