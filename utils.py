from fastapi import UploadFile
from PIL import Image
import uuid


def save_image(image: UploadFile) -> str:
    IMG_DIR = "uploads/img"
    
    image_bytes = image.file.read()

    filename = uuid.uuid4()
    file_extension = image.filename.split('.')[1]

    image_path = f"{IMG_DIR}/{filename}.{file_extension}"

    #Save original photo
    with open(image_path, 'wb') as f:
        f.write(image_bytes)
    
    return image_path
    
        
    
    