import openai
import json

class voice2text:
    def __init__(self) -> None:
        self.openai_key = None
        pass
    
    def set_credentials_from_json(self, credentials_json_file=''):
        self.openai_key = self.read_key_from_json(credentials_json_file)
        openai.api_key = self.openai_key
        pass

    def read_key_from_json(self, filename):
        try:
            with open(filename, "r") as archivo:
                data = json.load(archivo)
                clave_key = data.get("key")
                if clave_key is not None:
                    return str(clave_key)
                else:
                    return None
        except FileNotFoundError:
            print(f"El archivo {filename} no se encuentra.")
            return None
        except KeyError:
            print(f"La clave 'key' no está presente en el archivo JSON.")
            return None
        except json.JSONDecodeError:
            print(f"El archivo {filename} no es un JSON válido.")
            return None
        
    def transcribe_audio_file(self, record_name=''):
        audio_file = open(record_name, 'rb')
        transcript = openai.Audio.transcribe('whisper-1', audio_file)
        return transcript['text']