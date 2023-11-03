from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from pathlib import Path
from scripts.py_.voice_to_text import voice2text  # Asegúrate de que la ruta de importación sea correcta

app = FastAPI()
last_file = ''
v2t = voice2text()  # Instancia de la clase voice2text
v2t.set_credentials_from_json('./credentials/openai_key.json')

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
        return JSONResponse(status_code=200, content={"transcription": text})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
