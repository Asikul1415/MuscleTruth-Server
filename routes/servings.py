from typing import List

from fastapi import APIRouter, Depends, File, Form, HTTPException, status
from sqlalchemy import desc
from sqlalchemy.orm import Session

import models, schemas
from database import get_db
from login import (
    get_current_user,
)



servings_router = APIRouter(prefix='/api/servings')


@servings_router.get("", response_model=List[schemas.ServingBase])
def get_meal_servings(meal_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_items = db.query(models.Serving).filter(models.Serving.meal_id == meal_id)
    if(not db_items):
        raise HTTPException(
            status_code=status.HTTP_204_NO_CONTENT
        )
    
    return db_items.all()

@servings_router.get("/recent", response_model=List[schemas.RecentServing])
def get_recent_servings(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_items = db.query(models.RecentServing).filter(models.RecentServing.user_id == current_user.id).order_by(desc(models.RecentServing.use_date))

    return db_items.limit(50).all()

@servings_router.post("/recent", response_model=schemas.RecentServing)
def add_recent_serving(serving_id: int = Form(...), current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_item = models.RecentServing(
        serving_id = serving_id,
        user_id = current_user.id
    )

    db.add(db_item)
    db.commit()
    db.refresh(db_item)

    return db_item

@servings_router.delete("/recent/{serving_id}", response_model=bool)
def delete_recent_serving(serving_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_item = db.query(models.RecentServing).filter(models.RecentServing.serving_id == serving_id).first()

    db.delete(db_item)
    db.commit()

    return True

@servings_router.get("/{serving_id}", response_model=schemas.ServingBase)
def get_serving(serving_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_item = db.query(models.Serving).filter(models.Serving.id == serving_id).first()
    if(not db_item):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Такой порции не существует!"
        )

    return db_item

@servings_router.post("", response_model=schemas.ServingBase)
def add_serving(serving: schemas.ServingCreate, meal_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_item = models.Serving(
        user_id = current_user.id,
        meal_id = meal_id,
        product_id = serving.product_id,
        product_amount = serving.product_amount
    )

    db.add(db_item)
    db.commit()
    db.refresh(db_item)

    return db_item

@servings_router.put("/{serving_id}", response_model=schemas.AddResponse)
def update_serving(serving: schemas.ServingCreate, serving_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_item = db.query(models.Serving).filter(models.Serving.id == serving_id).first()
    if(not db_item):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Такой порции не существует!",
        )
    elif(db_item.user_id != current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Порцию может редактировать только пользователь, её добавивший!",
        )
    
    db_item.product_id = serving.product_id
    db_item.product_amount = serving.product_amount

    db.commit()
    db.refresh(db_item)

    return db_item

@servings_router.delete("/{serving_id}", response_model=schemas.AddResponse)
def delete_serving(serving_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    serving = db.query(models.Serving).filter(models.Serving.id == serving_id).first()
    if(not serving):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Такой порции не существует!",
        )
    elif(serving.user_id != current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Порцию может удалить только пользователь, её добавивший!",
        )
    
    db.delete(serving)
    db.commit()

    recent_serving = db.query(models.RecentServing).filter(models.RecentServing.serving_id == serving_id).first()
    db.delete(recent_serving)
    db.commit()

    return serving
