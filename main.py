from datetime import timedelta

from fastapi import FastAPI, APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import uvicorn

import models, schemas
from database import get_db, SessionLocal, engine
from login import (
    authenticate_user, 
    get_current_user,
    create_JWT_token,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

models.Base.metadata.create_all(bind=engine)
app = FastAPI()
api_router = APIRouter(prefix='/api')



@api_router.post("/auth/register", response_model=schemas.AddResponse)
def create_user(user: schemas.UserBase, db: Session = Depends(get_db)):
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

@api_router.post("/auth/login", response_model=schemas.Token)
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

@api_router.post("/weightings", response_model=schemas.AddResponse)
async def add_weighting(weighting: schemas.WeightingCreate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_item = models.Weighting(
        user_id = current_user.id,
        result = weighting.result,
        picture = weighting.picture,
        creation_date = weighting.creation_date
    )

    db.add(db_item)
    db.commit()
    db.refresh(db_item)

    return db_item

@api_router.post("/meals", response_model=schemas.AddResponse)
async def add_meal(meal: schemas.MealCreate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_item = models.Meal(
        user_id = current_user.id,
        picture = meal.picture,
        creation_date = meal.creation_date
    )

    db.add(db_item)
    db.commit()
    db.refresh(db_item)

    return db_item

@api_router.post("/meals/{meal_id}/products", response_model=schemas.AddResponse)
async def add_serving(serving: schemas.ServingCreate, meal_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_item = models.Serving(
        meal_id = meal_id,
        product_id = serving.product_id,
        product_amount = serving.product_amount
    )

    db.add(db_item)
    db.commit()
    db.refresh(db_item)

    return db_item

@api_router.post("/products", response_model=schemas.AddResponse)
async def add_product(product: schemas.ProductCreate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_item = models.Product(
        user_id = current_user.id,
        title = product.title,
        proteins = product.proteins,
        fats = product.fats,
        carbs = product.carbs,
        picture = product.picture,
    )

    db.add(db_item)
    db.commit()
    db.refresh(db_item)

    return db_item

app.include_router(api_router)
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)