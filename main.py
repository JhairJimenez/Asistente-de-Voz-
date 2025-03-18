import ollama
from audio.escucha import escuchar
from audio.habla import hablar, interrumpir, tts_thread, audio_queue  # Importar audio_queue
from config import MODEL_OLLAMA, MAX_HISTORY

conversation_history = []
system_prompt = {
    "role": "system",
    "content": "Responde de manera natural, como si estuvieras teniendo una conversación casual. Usa un tono amigable y evita respuestas demasiado largas. y evita usar los astericos a toda costa, ademas escribe en texto plano sin saltos de lineas. es una orden."
}
conversation_history.append(system_prompt)

print("\U0001F916 IA Local con Ollama (Mantén 'N' para hablar, di 'salir' para terminar, 'borrar' para limpiar historial)\n")

def main():
    hablar("Hola, soy tu asistente. Mantén presionada la tecla N para hablarme.")
    global conversation_history
    try:
        while True:
            user_input = escuchar()
            if not user_input:
                continue

            if "salir" in user_input:
                hablar("Hasta luego")
                break
            elif "borrar" in user_input:
                conversation_history.clear()
                conversation_history.append(system_prompt)
                interrumpir()
                hablar("Historial borrado")
                continue

            interrumpir()  # Detener cualquier respuesta previa
            conversation_history.append({"role": "user", "content": user_input})
            if len(conversation_history) > MAX_HISTORY * 2:
                conversation_history = [system_prompt] + conversation_history[-(MAX_HISTORY * 2 - 1):]

            print("IA: ", end="", flush=True)
            response_text = ""
            buffer_text = ""

            response_stream = ollama.chat(model=MODEL_OLLAMA, messages=conversation_history, stream=True)
            for chunk in response_stream:
                content = chunk.get("message", {}).get("content", "")
                print(content, end="", flush=True)
                response_text += content
                buffer_text += content
                if any(char in content for char in [".", "!", "?"]):
                    hablar(buffer_text.strip())
                    buffer_text = ""

            if buffer_text.strip():
                hablar(buffer_text.strip())

            print("\n")
            conversation_history.append({"role": "assistant", "content": response_text})
    finally:
        audio_queue.put(None)  # Usar la cola importada
        tts_thread.join()

if __name__ == "__main__":
    main()