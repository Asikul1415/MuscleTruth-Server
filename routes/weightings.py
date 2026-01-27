from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

import models, schemas
from database import get_db
from login import (
    get_current_user,
)



weightings_router = APIRouter(prefix='/api/weightings')


@weightings_router.get("", response_model=List[schemas.WeightingBase])
def get_weightings(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_items = db.query(models.Weighting).filter(models.Weighting.user_id == current_user.id).all()
    if(not db_items):
        raise HTTPException(
            status_code=status.HTTP_204_NO_CONTENT,
            detail="Список взвешиваний пуст!"
        )
    
    return db_items

@weightings_router.get("/{weighting_id}", response_model=schemas.WeightingBase)
def get_weighting(weighting_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_item = db.query(models.Weighting).filter(models.Weighting.id == weighting_id).first()
    if(not db_item):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Такого взвешивания не существует!"
        )
    elif(db_item.user_id != current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Взвешивание может просматривать только пользователь, его добавивший!",
        )
    
    return db_item

@weightings_router.post("", response_model=schemas.AddResponse)
def add_weighting(weighting: schemas.WeightingCreate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
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

@weightings_router.put("/{weighting_id}", response_model=schemas.AddResponse)
def update_weighting(weighting: schemas.WeightingUpdate, weighting_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_item = db.query(models.Weighting).filter(models.Weighting.id == weighting_id).first()
    if(not db_item):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Такого взвешивания не существует!"
        )
    elif(db_item.user_id != current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Взвешивание может просматривать только пользователь, его добавивший!",
        )
    
    db_item.result = weighting.result
    db_item.picture = weighting.picture

    db.commit()
    db.refresh(db_item)

    return db_item

@weightings_router.delete("/{weighting_id}", response_model=schemas.AddResponse)
def delete_weighting(weighting_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_item = db.query(models.Weighting).filter(models.Weighting.id == weighting_id).first()
    if(not db_item):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Такого взвешивания не существует!"
        )
    elif(db_item.user_id != current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Взвешивание может удалить только пользователь, его добавивший!",
        )

    db.delete(db_item)
    db.commit()

    return db_item