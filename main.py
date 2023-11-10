from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from pathlib import Path
from scripts.py_.voice_to_text import voice2text
from scripts.py_.text_to_image import StableDiffusionAPIConnection
from fastapi.middleware.cors import CORSMiddleware
from io import BytesIO
import base64
from pydantic import BaseModel
from datetime import datetime
import csv

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


new_row = {
    'record_name' : "", 
    'prompt' : "",
    's3_bucket_name' : "",
    's3_filename': "",
    'init_upload_audio': "",
    'init_save_trans': "",
    'final_process_image' : ""
}

sd_generator = StableDiffusionAPIConnection(
    api_key_path=sd_path,
    s3_credentials_csv_path=s3_path,
    bucket_name=bucket_name
)

@app.post("/upload/")
async def upload_audio(file: UploadFile = None):
    global last_file
    last_file = file.filename #record name

    if not file:
        raise HTTPException(status_code=400, detail="File not provided")

    try:
        filename = file.filename
        new_row['record_name'] = last_file
        init_upload_audio = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_row['init_upload_audio'] = init_upload_audio
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

        # ----------------------------------------------------------------
        init_save_trans = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_row['init_save_trans'] = init_save_trans
        # ----------------------------------------------------------------
        new_row['prompt'] = text
        # ----------------------------------------------------------------



        print(text) #guardarlo
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

        s3_bucket_name = sd_generator.s3_bucket_name #route name
        s3_filename = sd_generator.s3_filename
        new_row['s3_bucket_name'] = s3_bucket_name
        new_row['s3_filename'] = s3_filename
        final_process_image = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_row['final_process_image'] = final_process_image
        file_csv = 'data_all.csv'

        new_row['prompt'] = new_row['prompt'].strip()

        print(new_row)
        
        with open(file_csv, 'a', newline='') as archivo_csv:
            w_csv = csv.DictWriter(archivo_csv, fieldnames=new_row.keys())
            w_csv.writerow(new_row)

        return {"image": img_str}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    print('local')
    uvicorn.run(app, host="0.0.0.0", port=8000)




# Imprimir el DataFrame vacío

