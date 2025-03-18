import speech_recognition as sr
import keyboard
import time

def escuchar():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    print("\nMantén presionada la tecla 'N' para hablar...")
    
    while True:
        if keyboard.is_pressed("n"):
            with mic as source:
                print("🎤 Escuchando mientras mantengas 'N' presionada...")
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                try:
                    audio = recognizer.listen(source, timeout=None, phrase_time_limit=30)
                    texto = recognizer.recognize_google(audio, language="es-ES").lower()
                    print(f"🎙️ Detectado: {texto}")
                    return texto
                except sr.UnknownValueError:
                    print("No entendí lo que dijiste.")
                    return ""
                except sr.RequestError as e:
                    print(f"Error con el servicio de reconocimiento: {e}")
                    return ""
        time.sleep(0.1)  # Pequeña pausa para no saturar la CPU