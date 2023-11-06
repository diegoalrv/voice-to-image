from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from pathlib import Path
from scripts.py_.voice_to_text import voice2text
from scripts.py_.text_to_image import StableDiffusionAPIConnection
from fastapi.middleware.cors import CORSMiddleware
from io import BytesIO
import base64
from pydantic import BaseModel

app = FastAPI()

# Configura el middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite todas las origenes
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos los métodos
    allow_headers=["*"],  # Permite todos los headers
)

last_file = ''
v2t = voice2text()  # Instancia de la clase voice2text
v2t.set_credentials_from_json('./credentials/openai_key.json')
v2t.start_client()

s3_path = './credentials/voice_to_image_accessKeys.csv'
sd_path = './credentials/stability-ai-api-key.json'
bucket_name = 'stable-diffusion-city-images'

sd_generator = StableDiffusionAPIConnection(
    api_key_path=sd_path,
    s3_credentials_csv_path=s3_path,
    bucket_name=bucket_name
)

@app.post("/upload/")
async def upload_audio(file: UploadFile = None):
    global last_file
    last_file = file.filename
    if not file:
        raise HTTPException(status_code=400, detail="File not provided")

    try:
        filename = file.filename
        file_path = f"./data/output/records/{filename}"
        with open(file_path, "wb") as buffer:
            buffer.write(file.file.read())
        return JSONResponse(status_code=200, content={"message": "File uploaded successfully!"})
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/transcribe/")
async def transcribe_audio():
    global last_file
    if last_file == '':
        raise HTTPException(status_code=400, detail="No audio file has been uploaded yet.")
    
    try:
        file_path = f"./data/output/records/{last_file}"
        text = v2t.transcribe_audio_file(record_name=file_path)
        print(text)
        return JSONResponse(status_code=200, content={"transcription": text})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
class Prompt(BaseModel):
    prompt: str

@app.post("/generate-image/")
async def generate_image_endpoint(prompt: Prompt):
    print(prompt.prompt)
    try:
        final_image = sd_generator.process_image(prompt.prompt)
        print(final_image)
        img_byte_arr = BytesIO()
        final_image.save(img_byte_arr, format='PNG')
        img_str = base64.b64encode(img_byte_arr.getvalue()).decode()

        return {"image": img_str}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
