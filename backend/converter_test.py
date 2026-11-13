import io
from fastapi import FastAPI, File, UploadFile
from converter import file_to_str

app = FastAPI()

@app.post("/convert")
async def convert(file: UploadFile =  File(...)):
    return {"result": file_to_str(file, await file.read())}

# uvicorn converter_test:app --reload