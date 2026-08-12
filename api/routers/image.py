import pytesseract

from fastapi import APIRouter, UploadFile, File, HTTPException
from PIL import Image
from io import BytesIO

from tools import search_products

pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

router = APIRouter(tags=["Image"])


@router.post("/image/analyze")
async def analyze_image(image: UploadFile = File(...)):

    if not image.content_type:
        raise HTTPException(
            status_code=400,
            detail="Invalid image."
        )

    if not image.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="Please upload an image file."
        )

    image_bytes = await image.read()

    if not image_bytes:
        raise HTTPException(
            status_code=400,
            detail="The uploaded image is empty."
        )

    try:
        img = Image.open(
            BytesIO(image_bytes)
        ).convert("RGB")
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Could not read the uploaded image."
        )

    try:
        from PIL import ImageEnhance, ImageFilter

        # Make image larger for OCR
        width, height = img.size
        img = img.resize(
            (width * 2, height * 2)
        )

        # Improve contrast and sharpness
        img = ImageEnhance.Contrast(img).enhance(2)
        img = ImageEnhance.Sharpness(img).enhance(2)

        # Try OCR with a few different configurations
        extracted_text = ""

        for config in ["--psm 6", "--psm 11", "--psm 12"]:
            text = pytesseract.image_to_string(
                img,
                config=config
            ).strip()

            if text:
                extracted_text = text
                break

    except Exception as error:
        print("OCR ERROR:", error, flush=True)

        raise HTTPException(
            status_code=500,
            detail=f"OCR failed: {error}"
        )

    print(
        "IMAGE OCR:",
        repr(extracted_text),
        flush=True
    )

    if not extracted_text:
        return {
            "identified_product": None,
            "message": "I could not detect product text in this image."
        }

    result = search_products(extracted_text)

    if isinstance(result, dict) and result.get("message"):
        for word in extracted_text.split():

            if len(word) >= 3:

                result = search_products(word)

                if isinstance(result, list) and result:
                    break

    return {
        "identified_product": extracted_text,
        "catalog": result
    }