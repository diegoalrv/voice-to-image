from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from pathlib import Path

app = FastAPI()

@app.post("/upload/")
async def upload_audio(file: UploadFile = None):
    print(file.filename)
    if not file:
        raise HTTPException(status_code=400, detail="File not provided")

    try:
        filename = file.filename
        with open(f"./data/output/records/{filename}", "wb") as buffer:
            buffer.write(file.file.read())
        return JSONResponse(status_code=200, content={"message": "File uploaded successfully!"})
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
    # uvicorn.run(app)
