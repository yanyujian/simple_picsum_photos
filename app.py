'''
  * author 冯自立
  * created at : 2025-06-27 10:14:08
  * description: 
'''
import random as pyrandom
import hashlib
from typing import Optional

from fastapi import FastAPI, Response, Query
from PIL import Image
from io import BytesIO
import uvicorn
import os

app = FastAPI()


def realWorker(width, height, random):
    # Determine file path
    if random:
        file = max(1, min(random, 3))  # force file in [1,3]
        BASE_IMAGE_PATH = f"./pictures/{file}.png"
    else:
        BASE_IMAGE_PATH = pyrandom.choice(['./pictures/1.png', './pictures/2.png', './pictures/3.png'])

    if not os.path.exists(BASE_IMAGE_PATH):
        return {"error": f"Base image not found: {BASE_IMAGE_PATH}"}

    with Image.open(BASE_IMAGE_PATH) as img:
        img = img.convert("RGB")
        src_width, src_height = img.size
        aspect_ratio = width / height
        src_ratio = src_width / src_height

        if aspect_ratio > src_ratio:
            new_height = int(src_width / aspect_ratio)
            offset = (src_height - new_height) // 2
            crop_box = (0, offset, src_width, offset + new_height)
        else:
            new_width = int(src_height * aspect_ratio)
            offset = (src_width - new_width) // 2
            crop_box = (offset, 0, offset + new_width, src_height)

        cropped = img.crop(crop_box).resize((width, height))
        buffer = BytesIO()
        cropped.save(buffer, format="JPEG")
        image_bytes = buffer.getvalue()

        # Caching headers
        etag = hashlib.md5(image_bytes).hexdigest()
        headers = {
            "Cache-Control": "public, max-age=86400",
            "ETag": etag
        }

        return Response(image_bytes, media_type="image/jpeg", headers=headers)


@app.get("/{width}/{height}")
def crop_image(
        width: int,
        height: int,
        random: Optional[int] = Query()
):
    try:
        return realWorker(width, height, random)
    except Exception as e:
        print(f"Error processing image: {e}")
        return Response(content=str(e), status_code=500)


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=33536)
