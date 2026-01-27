from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

import models, schemas
from database import get_db
from login import (
    get_current_user,
)



users_router = APIRouter(prefix='/api/users')


@users_router.get("/me", response_model=schemas.UserBase)
def get_user_info(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    if(not current_user):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Вы не авторизованы!"
        )

    return current_user

@users_router.put("/me", response_model=schemas.AddResponse)
def update_user_info(user: schemas.UserBase, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    if(not current_user):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Вы не авторизованы!"
        )
    
    current_user.name = user.name
    current_user.email = user.email
    current_user.password = models.User.get_password_hash(user.password)
    current_user.age = user.age
    current_user.profile_picture = user.profile_picture

    db.commit()
    db.refresh(current_user)

    return current_user