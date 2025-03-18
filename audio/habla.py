import os
import queue
import threading
import asyncio
import pygame
import edge_tts
import time
from config import VOICE, RATE, PITCH, VOLUME

audio_queue = queue.Queue(maxsize=5)
tts_task_queue = queue.Queue()

# Variable global para controlar interrupciones
stop_generation = False

def speak_worker():
    pygame.mixer.init()
    while True:
        audio_file = audio_queue.get()
        if audio_file is None:
            break
        try:
            pygame.mixer.music.load(audio_file)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                if stop_generation:
                    pygame.mixer.music.stop()
                    break
                time.sleep(0.1)
            pygame.mixer.music.stop()
            pygame.mixer.quit()
            pygame.mixer.init()
        except Exception:
            pass  # Silenciar errores
        finally:
            if os.path.exists(audio_file):
                os.remove(audio_file)
            audio_queue.task_done()

async def generate_audio(text):
    if not text.strip():
        return
    audio_file = f"response_{int(time.time() * 1000)}.mp3"
    if os.path.exists(audio_file):
        return
    communicate = edge_tts.Communicate(text, VOICE, rate=RATE, pitch=PITCH, volume=VOLUME)
    await communicate.save(audio_file)
    if os.path.exists(audio_file) and os.path.getsize(audio_file) > 0:
        audio_queue.put(audio_file)

def run_async_in_thread(text):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(generate_audio(text))
    loop.close()

tts_thread = threading.Thread(target=speak_worker, daemon=True)
tts_thread.start()

def hablar(texto):
    if not texto.strip():
        return
    threading.Thread(target=run_async_in_thread, args=(texto,), daemon=True).start()

def esperar_fin_audio():
    while not (tts_task_queue.empty() and audio_queue.empty()):
        time.sleep(0.5)

def interrumpir():
    global stop_generation
    stop_generation = True
    pygame.mixer.music.stop()
    with audio_queue.mutex:
        audio_queue.queue.clear()
    for file in os.listdir():
        if file.startswith("response_") and file.endswith(".mp3"):
            try:
                os.remove(file)
            except Exception:
                pass
    stop_generation = False