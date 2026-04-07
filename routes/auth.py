from datetime import timedelta

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

import models, schemas
from database import get_db
from login import (
    authenticate_user, 
    create_JWT_token,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
import utils
import json


auth_router = APIRouter(prefix='/api/auth')


@auth_router.post("/register", response_model=schemas.Token)
def create_user(user: str = Form(...), image: UploadFile = File(None), db: Session = Depends(get_db)):
    data_dict = json.loads(user)
    user_create = schemas.UserBase(**data_dict)

    image_path = None
    if image and image.filename:
        paths = utils.save_image(image)
        image_path = paths

    db_user = db.query(models.User).filter(models.User.email == user_create.email).first()
    if db_user:
        raise HTTPException(
            status_code=400, 
            detail="Данная почта уже зарегистрирована!")
    
    db_item = models.User(
        name=user_create.name,
        email=user_create.email,
        password= models.User.get_password_hash(user_create.password),
        age=user_create.age,
        profile_picture=image_path
    )
    
    db.add(db_item)
    db.commit()
    db.refresh(db_item)

    access_token = create_JWT_token(
        data={"sub": user_create.email}, 
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": db_item.id
    }

@auth_router.post("/login", response_model=schemas.Token)
def login(user_data: schemas.UserLogin,  db: Session = Depends(get_db)):
    user = authenticate_user(db, user_data.email, user_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверные данные!",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_JWT_token(
        data={"sub": user.email}, 
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id
    }