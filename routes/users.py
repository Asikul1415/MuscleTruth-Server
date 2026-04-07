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

@users_router.post("/check-email", response_model=schemas.BoolResponse)
def check_user_email(email: schemas.CheckEmail, db: Session = Depends(get_db)):

    db_item = db.query(models.User).filter(models.User.email == email.email).first()
    if(db_item):
        return schemas.BoolResponse(response=True)

    return schemas.BoolResponse(response=False)

@users_router.get("/me", response_model=schemas.UserRequest)
def get_user_info(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):

    if(not current_user):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Вы не авторизованы!"
        )

    user = schemas.UserRequest(
        id = current_user.id,
        name=current_user.name,
        email=current_user.email,
        password = current_user.password,
        age = current_user.age,
        profile_picture=current_user.profile_picture
    )

    return user

@users_router.post("/me/check-password", response_model=schemas.BoolResponse)
def check_user_password(user:schemas.UserPassword ,current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):

    if(not current_user):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Вы не авторизованы!"
        )
    
    return schemas.BoolResponse(response=models.User.verify_password(current_user, user.password))

@users_router.put("/me", response_model=bool)
def update_user_info(user: str = Form(...), image: UploadFile = File(None), current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):

    if(not current_user):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Вы не авторизованы!"
        )
    
    data_dict = json.loads(user)
    user_create = schemas.UserBase(**data_dict)

    image_path = None
    if image and image.filename:
        paths = utils.save_image(image)
        image_path = paths
    
    current_user.name = user_create.name
    current_user.email = user_create.email
    current_user.password = models.User.get_password_hash(user_create.password)
    current_user.age = user_create.age
    current_user.profile_picture = image_path

    db.commit()
    db.refresh(current_user)

    return True