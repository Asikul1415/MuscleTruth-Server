import json
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

import models, schemas
from database import get_db
from login import (
    get_current_user,
)
import utils



users_router = APIRouter(prefix='/api/users')

@users_router.post("/check-email", response_model=bool)
def check_user_email(email: str = Form(...), db: Session = Depends(get_db)):

    db_item = db.query(models.User).filter(models.User.email == email).first()
    return db_item != None

@users_router.get("/me", response_model=schemas.UserBase)
def get_user_info(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):

    if(not current_user):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Вы не авторизованы!"
        )

    return current_user

@users_router.post("/me/check-password", response_model=bool)
def check_user_password(password: str = Form(...), current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):

    if(not current_user):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Вы не авторизованы!"
        )
    
    return models.User.verify_password(current_user, password)

@users_router.put("/me", response_model=bool)
def update_user_info(user: str = Form(...), image: UploadFile = File(None), current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):

    if(not current_user):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Вы не авторизованы!"
        )
    
    data_dict = json.loads(user)
    updated_user_info = schemas.UserUpdate(**data_dict)

    image_path = None
    if image and image.filename:
        paths = utils.save_image(image)
        image_path = paths
    
    if(updated_user_info.name and len(updated_user_info.name) > 3):
        current_user.name = updated_user_info.name
    if(updated_user_info.email and len(updated_user_info.email) > 5):
        current_user.email = updated_user_info.email
    if(updated_user_info.password and len(updated_user_info.password) > 8):
        current_user.password = models.User.get_password_hash(updated_user_info.password)
    if(updated_user_info.age and updated_user_info.age > 6 and updated_user_info.age < 130):
        current_user.age = updated_user_info.age
    if(image_path):
        current_user.profile_picture = image_path

    db.commit()
    db.refresh(current_user)

    return True