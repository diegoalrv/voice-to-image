import pyaudio
import wave
from datetime import datetime
import openai
import json

def get_timestamp():
    current_time = datetime.now()
    formatted_time = current_time.strftime('%d%m%y_%H%M%S')
    return formatted_time

def list_audio_devices():
    p = pyaudio.PyAudio()
    info = p.get_host_api_info_by_index(0)
    num_devices = info.get('deviceCount')
    
    print("Dispositivos de entrada de audio disponibles:")
    
    for i in range(num_devices):
        device_info = p.get_device_info_by_host_api_device_index(0, i)
        device_name = device_info['name']
        print(f"Índice {i}: {device_name}")

# def record_audio_with_device(filename, seconds, device_index):
#     # Configuración de la grabación
#     FORMAT = pyaudio.paInt16
#     CHANNELS = 1
#     RATE = 44100
#     CHUNK = 1024
    
#     # Inicializar el objeto PyAudio
#     audio = pyaudio.PyAudio()

#     # Abrir el flujo de entrada de audio con el dispositivo seleccionado
#     stream = audio.open(format=FORMAT, channels=CHANNELS,
#                         rate=RATE, input=True,
#                         frames_per_buffer=CHUNK,
#                         input_device_index=device_index)

#     print(f"Grabando durante {seconds} segundos con el dispositivo {device_index}...")

#     frames = []

#     # Grabar audio en trozos y guardar los fragmentos en la lista de frames
#     for _ in range(0, int(RATE / CHUNK * seconds)):
#         data = stream.read(CHUNK)
#         frames.append(data)

#     print("¡Grabación completa!")

#     # Detener y cerrar el flujo de audio
#     stream.stop_stream()
#     stream.close()

#     # Terminar PyAudio
#     audio.terminate()

#     # Guardar la grabación en un archivo WAV
#     with wave.open(filename, 'wb') as wf:
#         wf.setnchannels(CHANNELS)
#         wf.setsampwidth(audio.get_sample_size(FORMAT))
#         wf.setframerate(RATE)
#         wf.writeframes(b''.join(frames))

def record_audio_with_device(filename, device_index):
    # Configuración de la grabación
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    CHUNK = 1024
    
    # Inicializar el objeto PyAudio
    audio = pyaudio.PyAudio()

    # Abrir el flujo de entrada de audio con el dispositivo seleccionado
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK,
                        input_device_index=device_index)

    print(f"Grabando con el dispositivo {device_index}...")
    print("Presiona Enter para detener la grabación.")
    
    frames = []

    # Comienza a grabar indefinidamente hasta que se presione Enter
    try:
        while True:
            print('miau')
            data = stream.read(CHUNK)
            frames.append(data)
    except KeyboardInterrupt:
        pass

    print("¡Grabación completa!")

    # Detener y cerrar el flujo de audio
    stream.stop_stream()
    stream.close()

    # Terminar PyAudio
    audio.terminate()

    # Guardar la grabación en un archivo WAV
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))


def extraer_key_de_json(nombre_archivo):
    try:
        with open(nombre_archivo, "r") as archivo:
            data = json.load(archivo)
            clave_key = data.get("key")
            if clave_key is not None:
                return str(clave_key)
            else:
                return None
    except FileNotFoundError:
        print(f"El archivo {nombre_archivo} no se encuentra.")
        return None
    except KeyError:
        print(f"La clave 'key' no está presente en el archivo JSON.")
        return None
    except json.JSONDecodeError:
        print(f"El archivo {nombre_archivo} no es un JSON válido.")
        return None

archivo_json = "openai_key.json"
valor_key = extraer_key_de_json(archivo_json)
openai.api_key = valor_key

# Ejemplo de uso:
if __name__ == "__main__":
    ts = get_timestamp()
    record_name = f'./data/output/record_{ts}.wav'
    selected_device_index = 1  # Reemplaza esto con el índice del dispositivo que desees utilizar
    # record_audio_with_device(record_name, 5, selected_device_index)
    record_audio_with_device(record_name, selected_device_index)
    audio_file = open(record_name, 'rb')
    transcript = openai.Audio.transcribe('whisper-1', audio_file)

    print(transcript['text'])