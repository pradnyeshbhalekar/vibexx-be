import base64
from io import BytesIO
from PIL import Image

def decode_base64_image(image_data: str) -> Image.Image:
    if "," in image_data:
        image_data = image_data.split(",")[1]
    img_bytes = base64.b64decode(image_data)
    return Image.open(BytesIO(img_bytes)).convert("RGB")

print("Decode function looks ok.")
