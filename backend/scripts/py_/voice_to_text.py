import openai
import json
import os

class voice2text:
    def __init__(self) -> None:
        self.openai_key = None
        pass
    
    def set_credentials_from_json(self, credentials_json_file=''):
        # print(self.openai_key)
        # openai.api_key = self.openai_key
        pass

    def start_client(self):
        self.openai_key = os.getenv("OPENAI_API_KEY")
        print(self.openai_key)
        self.client = openai.OpenAI(api_key=self.openai_key)
        # self.client = openai.OpenAI()

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
        transcript = self.client.audio.transcriptions.create(
            model='whisper-1',
            file=audio_file,
            response_format="text",
        )
        print(transcript)
        return transcript