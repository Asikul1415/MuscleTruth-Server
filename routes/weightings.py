import datetime
from datetime import datetime, timedelta
from typing import List

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy import Date, Numeric, cast, func
from sqlalchemy.orm import Session

import models, schemas
from database import get_db
from login import (
    get_current_user,
)
import utils
import json


weightings_router = APIRouter(prefix='/api/weightings')


@weightings_router.get("", response_model=List[schemas.WeightingBase])
def get_weightings(start_date: str=None, end_date:str=None, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    
    db_items = db.query(models.Weighting).filter(models.Weighting.user_id == current_user.id)

    if(start_date != None):
        start = datetime.fromisoformat(start_date).date()
        end = datetime.fromisoformat(end_date).date()
        
        db_items = db_items.filter(
            models.Weighting.user_id == current_user.id).filter(
            func.date(models.Weighting.creation_date) >= start).filter(
            func.date(models.Weighting.creation_date) <= end)

    if(not db_items):
        raise HTTPException(
            status_code=status.HTTP_204_NO_CONTENT,
            detail="Список взвешиваний пуст!"
        )
    
    return db_items.all()

@weightings_router.get("/last", response_model=schemas.WeightingBase|None)
def get_weightings(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):

    db_items = db.query(models.Weighting).filter(models.Weighting.user_id == current_user.id).order_by(models.Weighting.id.desc())

    if(not db_items):
        raise HTTPException(
            status_code=status.HTTP_204_NO_CONTENT,
            detail="Список взвешиваний пуст!"
        )
    
    weighting = db_items.first()
    if(weighting != None):
        return schemas.WeightingBase(
            id = weighting.id,
            user_id=weighting.user_id,
            result=weighting.result,
            picture=weighting.picture,
            creation_date=weighting.creation_date
        ) 
    
    raise HTTPException(
        status_code=status.HTTP_204_NO_CONTENT,
        detail="Добавьте первое взвешивание!"
    )

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

@weightings_router.get("/chart/month")
def get_weighting_chart_data(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):

    end = datetime.today()
    start = end - timedelta(days=31)

    weekly_stats = db.query(
        func.date_trunc('day', models.Weighting.creation_date).cast(Date).label('day'),
        func.round(cast(func.avg(models.Weighting.result), Numeric), 2).label('average_weight')
    ).filter(
        models.Weighting.user_id == current_user.id and models.Weighting.creation_date >= start
    ).group_by(
        func.date_trunc('day', models.Weighting.creation_date)
    ).order_by(
        func.date_trunc('day', models.Weighting.creation_date)
    ).limit(31).all()

    data = [
        {
            "day": str(r.day),
            "average_weight": float(r.average_weight)}
        for r in weekly_stats
    ]
    for dat in data:
        print(dat)
    
    return data  # JSON

@weightings_router.get("/chart/year")
def get_weighting_chart_data(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):

    end = datetime.today()
    start = end - timedelta(days=365)

    weekly_stats = db.query(
        func.date_trunc('week', models.Weighting.creation_date).cast(Date).label('week_start'),
        func.round(cast(func.avg(models.Weighting.result), Numeric), 2).label('average_weight')
    ).filter(
        models.Weighting.user_id == current_user.id and models.Weighting.creation_date >= start
    ).group_by(
        func.date_trunc('week', models.Weighting.creation_date)
    ).order_by(
        func.date_trunc('week', models.Weighting.creation_date)
    ).limit(52).all()

    data = [
        {
            "week_start": str(r.week_start),
            "average_weight": float(r.average_weight)
        }
        for r in weekly_stats
    ]
    print(data)
    
    return data  # JSON


@weightings_router.post("", response_model=schemas.WeightingBase)
def add_weighting(weighting: str = Form(...), image: UploadFile = File(None), current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):

    data_dict = json.loads(weighting)
    weighting_create = schemas.WeightingCreate(**data_dict)

    image_path = None
    if image and image.filename:
        paths = utils.save_image(image)
        image_path = paths

    creation_date = weighting_create.creation_date
    if(creation_date == None):
        creation_date = func.now()

    db_item = models.Weighting(
        user_id = current_user.id,
        result = weighting_create.result,
        picture = image_path,
        creation_date = creation_date
    )

    db.add(db_item)
    db.commit()
    db.refresh(db_item)

    return db_item

@weightings_router.put("/{weighting_id}", response_model=bool)
def update_weighting(
    weighting_id: int, weighting: str = Form(...), 
    image: UploadFile = File(None), 
    current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):

    if(not current_user):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Вы не авторизованы!"
        )
    
    db_item = db.query(models.Weighting).filter(models.Weighting.id == weighting_id).first()
    if(not db_item):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Такого взвешивания не существует!"
        )
    elif(db_item.user_id != current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Взвешивание может изменить только пользователь, его добавивший!",
        )
    
    data_dict = json.loads(weighting)
    weighting_create = schemas.WeightingBase(**data_dict)

    image_path = None
    if image and image.filename:
        paths = utils.save_image(image)
        image_path = paths
    
    db_item.result = weighting_create.result
    if(image_path != None):
        db_item.picture = image_path

    db.commit()
    db.refresh(db_item)

    return True

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