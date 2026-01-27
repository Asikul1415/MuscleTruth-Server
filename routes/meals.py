from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

import models, schemas
from database import get_db
from login import (
    get_current_user,
)



meals_router = APIRouter(prefix='/api/meals')


@meals_router.get("", response_model=List[schemas.MealBase])
def get_meals(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_items = db.query(models.Meal).filter(models.Meal.user_id == current_user.id).all()
    if(not db_items):
        raise HTTPException(
            status_code=status.HTTP_204_NO_CONTENT,
            detail="Список приёмов пищи пуст!"
        )
    
    return db_items

@meals_router.get("/{meal_id}", response_model=schemas.MealBase)
def get_meal(meal_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_item = db.query(models.Meal).filter(models.Meal.id == meal_id).first()
    if(not db_item):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Такого приёма пищи не существует!"
        )
    elif(db_item.user_id != current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Приём пищи может просматривать только пользователь, его добавивший!",
        )
    
    return db_item

@meals_router.post("", response_model=schemas.AddResponse)
def add_meal(meal: schemas.MealCreate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_item = models.Meal(
        user_id = current_user.id,
        picture = meal.picture,
        creation_date = meal.creation_date
    )

    db.add(db_item)
    db.commit()
    db.refresh(db_item)

    return db_item

@meals_router.put("/{meal_id}", response_model=schemas.AddResponse)
def update_meal(meal: schemas.MealUpdate, meal_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_item = db.query(models.Meal).filter(models.Meal.id == meal_id).first()
    if(not db_item):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Такого приёма пищи не существует!"
        )
    elif(db_item.user_id != current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Приём пищи может редактировать только пользователь, его добавивший!",
        )
    
    db_item.picture = meal.picture

    db.commit()
    db.refresh(db_item)

    return db_item

@meals_router.delete("/{meal_id}", response_model=schemas.AddResponse)
def delete_meal(meal_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_item = db.query(models.Meal).filter(models.Meal.id == meal_id).first()
    if(not db_item):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Такого приёма пищи не существует!"
        )
    elif(db_item.user_id != current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Приём пищи может удалить только пользователь, его добавивший!",
        )
    
    db.delete(db_item)
    db.commit()

    return db_item