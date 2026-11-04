import io
from fastapi import FastAPI, File, UploadFile
from converter import file_to_str, get_file_group, ALLOWED_MIMETYPES

app = FastAPI()

@app.post("/convert")
async def convert(file: UploadFile =  File(...)):
    if file.content_type not in ALLOWED_MIMETYPES:
        return {"error": "Invalid file type!"}
    try:
        result = file_to_str(await file.read(), file.content_type)
    except Exception as e:
        return {"error": "Unable to read the file!", "error_text": str(e)}
    return {"result": result}

# uvicorn converter_test:app --reload