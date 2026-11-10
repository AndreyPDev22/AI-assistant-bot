import io
import numpy as np
import docx
import pymupdf
import zipfile
import xml.etree.ElementTree as ET
import easyocr
from PIL import Image
import pillow_avif
import pptx
import pandas
from faster_whisper import WhisperModel

from fastapi import UploadFile, HTTPException
from starlette.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_413_CONTENT_TOO_LARGE,
    HTTP_415_UNSUPPORTED_MEDIA_TYPE
)

ALLOWED_MIMETYPES = {
    "text/plain": "txt",
    "application/pdf": "pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation": "pptx",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "xlsx",
    "application/vnd.oasis.opendocument.text": "odt",
    "application/vnd.oasis.opendocument.spreadsheet": "ods",
    "image/jpeg": "jpeg",
    "image/png": "png",
    "image/webp": "webp",
    "image/avif": "avif",
    "audio/mpeg": "mp3"
}

MAX_FILE_SIZE = 10_485_760 # 10МБ

def get_file_group(file_type: str):
    if file_type in ("jpeg", "png", "webp", "avif"):
        return "image"
    if file_type in ("xlsx", "ods"):
        return "sheet"
    return file_type

# -----------------------
# ПОТОМ ОТСЮДА УБРАТЬ, НАПРИМЕР БРАТЬ ИЗ lifespan!!!
_image_reader = easyocr.Reader(["ru", "en"])
_audio_model =  WhisperModel("base", device="cpu", compute_type="int8")
# -----------------------

def file_to_str(
    file: UploadFile,
    file_content: bytes,
    image_reader: easyocr.Reader = _image_reader, # УБРАТЬ _image_reader
    audio_model: WhisperModel = _audio_model # УБРАТЬ _audio_model
):
    file_type = ALLOWED_MIMETYPES.get(file.content_type)
    if not file_type:
        raise HTTPException(HTTP_415_UNSUPPORTED_MEDIA_TYPE, "Формат файла не поддерживается!")
    if file.size > MAX_FILE_SIZE:
        raise HTTPException(HTTP_413_CONTENT_TOO_LARGE, "Размер файла превышает 10 МБ!")
    
    file_group = get_file_group(file_type)

    try:
        if file_group == "txt":
            return file_content.decode("utf-8")
        
        result = ""
        file_bytes = io.BytesIO(file_content)

        if file_group == "docx":
            doc = docx.Document(file_bytes)
            for paragraph in doc.paragraphs:
                result += paragraph.text + "\n"

        elif file_group == "pdf":
            doc = pymupdf.open(stream=file_bytes)
            for page in doc:
                result += page.get_text()
            doc.close()

        elif file_group == "odt":
            with zipfile.ZipFile(file_bytes) as zf:
                xml_content = zf.read('content.xml')
            root = ET.fromstring(xml_content)
            for elem in root.iter():
                if elem.tag.endswith('p') and elem.text:
                    result += elem.text

        elif file_group == "image":
            image = Image.open(file_bytes)
            if image.mode != "RGB":
                image = image.convert("RGB")
            image_np = np.array(image) 
            ocr_results = image_reader.readtext(image_np)
            result = "\n".join([text for (_, text, _) in ocr_results])
            image.close()

        elif file_group == "pptx":
            prs = pptx.Presentation(file_bytes)
            for slide in prs.slides:
                for shape in slide.shapes:
                    if shape.has_text_frame:
                        for paragraph in shape.text_frame.paragraphs:
                            for run in paragraph.runs:
                                if run.text.strip():
                                    result += run.text + "\n"

        elif file_group == "sheet":
            all_sheets = pandas.read_excel(file_bytes, sheet_name=None, engine = "openpyxl" if file_type == "xlsx" else "odf")
            for sheet_name, df in all_sheets.items():     
                sheet_text = df.to_csv(index=False) 
                result += sheet_text  + "\n"

        elif file_group == "mp3":
            segments, info = audio_model.transcribe(file_bytes, beam_size=5)
            result = "".join(segment.text for segment in segments).strip()

        file_bytes.close()
    except Exception as e:
        raise HTTPException(HTTP_400_BAD_REQUEST, f"Не удалось прочитать файл! ({e})")

    return result