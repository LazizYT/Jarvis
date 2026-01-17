import speech_recognition as sr
import pyaudio

print("="*50)
print("ТЕСТ УСТАНОВКИ PYAUDIO")
print("="*50)

# Тест PyAudio
print("1. Тестирую PyAudio...")
try:
    pa = pyaudio.PyAudio()
    print(f"✅ PyAudio работает! Версия: {pyaudio.__version__}")
    
    # Показываем устройства
    print(f"\n2. Найдено устройств: {pa.get_device_count()}")
    for i in range(pa.get_device_count()):
        info = pa.get_device_info_by_index(i)
        print(f"   [{i}] {info['name']} (входов: {info['maxInputChannels']})")
    
    pa.terminate()
    
except Exception as e:
    print(f"❌ Ошибка PyAudio: {e}")

# Тест микрофонов через speech_recognition
print("\n3. Тестирую микрофоны через speech_recognition...")
try:
    r = sr.Recognizer()
    mics = sr.Microphone.list_microphone_names()
    print(f"✅ Найдено микрофонов: {len(mics)}")
    
    for i, mic in enumerate(mics):
        print(f"   [{i}] {mic}")
        
    # Тест записи
    print("\n4. Тест записи...")
    with sr.Microphone() as source:
        print("   🔧 Настраиваюсь на шум...")
        r.adjust_for_ambient_noise(source, duration=1)
        
        print("   🎤 ГОВОРИТЕ СЕЙЧАС (5 секунд)...")
        try:
            audio = r.listen(source, timeout=5, phrase_time_limit=5)
            print("   ✅ Запись успешна!")
            
            # Попытка распознавания
            print("   🔍 Распознаю...")
            text = r.recognize_google(audio, language="ru-RU")
            print(f"   📝 Вы сказали: {text}")
            
        except sr.WaitTimeoutError:
            print("   ⏰ Не услышал голос")
        except sr.UnknownValueError:
            print("   ❌ Не удалось распознать речь")
        except Exception as e:
            print(f"   ⚠️ Ошибка: {e}")
            
except Exception as e:
    print(f"❌ Ошибка: {e}")

print("\n" + "="*50)
print("ТЕСТ ЗАВЕРШЕН!")
print("="*50)
input("Нажмите Enter для выхода...")