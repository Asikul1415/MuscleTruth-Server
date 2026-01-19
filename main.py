from datetime import timedelta

from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
import uvicorn

import models, schemas
from database import get_db, SessionLocal, engine
from login import (
    authenticate_user, 
    create_JWT_token,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

models.Base.metadata.create_all(bind=engine)
app = FastAPI()



@app.post("/users/register", response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(
            status_code=400, 
            detail="Email is already registered!")

    db_item = models.User(
        name=user.name,
        email=user.email,
        password= models.User.get_password_hash(user.password),
        age=user.age,
        profile_picture=user.profile_picture
    )
    
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.post("/users/login", response_model=schemas.Token)
async def login(user_data: schemas.UserLogin,  db: Session = Depends(get_db)):
    user = authenticate_user(db, user_data.email, user_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_JWT_token(
        data={"sub": user.email}, 
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)