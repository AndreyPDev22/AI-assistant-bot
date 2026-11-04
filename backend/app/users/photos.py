import warnings
from io import BytesIO

from fastapi import HTTPException, UploadFile
from PIL import Image, ImageOps, UnidentifiedImageError

MAX_PHOTO_BYTES = 5 * 1024 * 1024
MAX_PHOTO_PIXELS = 16_000_000
ALLOWED_FORMATS = {"JPEG", "PNG", "WEBP"}


def read_photo(photo: UploadFile | None) -> bytes | None:
    if photo is None:
        return None
    contents = photo.file.read(MAX_PHOTO_BYTES + 1)
    if len(contents) > MAX_PHOTO_BYTES:
        raise HTTPException(413, "Фото должно быть не больше 5 МБ")
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(BytesIO(contents)) as image:
                if image.format not in ALLOWED_FORMATS:
                    raise HTTPException(422, "Поддерживаются фото JPEG, PNG и WebP")
                if image.width * image.height > MAX_PHOTO_PIXELS:
                    raise HTTPException(
                        422, "Фото должно содержать не больше 16 миллионов пикселей"
                    )
                image = ImageOps.exif_transpose(image)
                image.thumbnail((512, 512))
                output = BytesIO()
                image.convert("RGB").save(output, format="JPEG", quality=85)
                return output.getvalue()
    except (
        UnidentifiedImageError,
        OSError,
        ValueError,
        Image.DecompressionBombError,
        Image.DecompressionBombWarning,
    ) as exc:
        raise HTTPException(422, "Не удалось прочитать фото") from exc
