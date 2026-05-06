from dataclasses import Field
from datetime import datetime, timedelta
from typing import List

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy import Date, Numeric, cast, func
from sqlalchemy.orm import Session

import schemas, models
from database import get_db
from login import (
    get_current_user,
)
import utils
import json



meals_router = APIRouter(prefix='/api/meals')


@meals_router.get("", response_model=List[schemas.MealBase])
def get_meals(start_date:str = None, end_date: str = None, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_items = db.query(models.Meal).filter(models.Meal.user_id == current_user.id)

    if(start_date != None and end_date != None):
        start = datetime.fromisoformat(start_date).date()
        end = datetime.fromisoformat(end_date).date()
        
        db_items = db_items.filter(
            func.date(models.Meal.creation_date) >= start).filter(
            func.date(models.Meal.creation_date) <= end)

    if(not db_items):
        raise HTTPException(
            status_code=status.HTTP_204_NO_CONTENT,
            detail="Список приёмов пищи пуст!"
        )
    
    return db_items.all()

@meals_router.get("/today", response_model=List[schemas.MealBase])
def get_today_meals(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_items = db.query(models.Meal).filter(models.Meal.user_id == current_user.id)

    today = datetime.now().date()
        
    db_items = db_items.filter(
        func.date(models.Meal.creation_date) >= today).filter(
        func.date(models.Meal.creation_date) <= today)

    if(not db_items):
        raise HTTPException(
            status_code=status.HTTP_204_NO_CONTENT,
            detail="Список приёмов пищи пуст!"
        )
    
    return db_items.all()

@meals_router.get("/{meal_type_id}/total", response_model=schemas.MealTypeTotal)
def get_meals(start_date:str, end_date: str, meal_type_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_items = db.query(models.Meal).filter(models.Meal.user_id == current_user.id)

    if(start_date != None and end_date != None):
        start = datetime.fromisoformat(start_date).date()
        end = datetime.fromisoformat(end_date).date()
        
        db_items = db_items.filter(
            models.Meal.meal_type_id == meal_type_id).filter(
            func.date(models.Meal.creation_date) >= start).filter(
            func.date(models.Meal.creation_date) <= end)
        meals = db_items.all()

        total_proteins = 0
        total_fats = 0
        total_carbs = 0
        
        for meal in meals:
            servings: List[models.Serving] = meal.servings
            for serving in servings:
                product: models.Product = serving.product

                total_proteins += product.proteins * serving.product_amount / 100
                total_fats += product.fats * serving.product_amount / 100
                total_carbs += product.carbs * serving.product_amount / 100
        total_calories = total_carbs * 4 + total_proteins * 4 + total_fats * 9

        return schemas.MealTypeTotal(
            proteins=total_proteins,
            fats=total_fats,
            carbs=total_carbs,
            total_calories=total_calories
        )

    raise HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        detail="Некорректный URL!"
    )
    
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

@meals_router.get("/chart/week")
def get_weightings_with_calories_week_info(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):

    end = datetime.today()
    start = end - timedelta(days=7)

    meals = db.query(models.Meal).filter(
        models.Meal.user_id == current_user.id,
        models.Meal.creation_date >= start,
        models.Meal.creation_date <= end
    ).all()


    meals_total_per_day = dict()
    for meal in meals:
        meal_calories = 0
        for serving in meal.servings:
            if serving.product:
                product: models.Product = serving.product
                meal_calories += (4 * product.proteins + 9 * product.fats + 4 * product.carbs) * (serving.product_amount / 100)
        day = meal.creation_date.date().isoformat()

        if(day not in meals_total_per_day.keys()):
            meals_total_per_day[day] = []
        meals_total_per_day[day].append(meal_calories)
    
    
    calories_per_day = []
    for day, values in sorted(meals_total_per_day.items()):
        calories_per_day.append({
            "day": day,
            "total_calories": sum(values)
        })

    return calories_per_day

@meals_router.get("/chart/month")
def get_weightings_with_calories_month_info(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):

    end = datetime.today()
    start = end - timedelta(days=31)

    meals = db.query(models.Meal).filter(
        models.Meal.user_id == current_user.id,
        models.Meal.creation_date >= start,
        models.Meal.creation_date <= end
    ).all()


    meals_total_per_day = dict()
    for meal in meals:
        meal_calories = 0
        for serving in meal.servings:
            if serving.product:
                product: models.Product = serving.product
                meal_calories += (4 * product.proteins + 9 * product.fats + 4 * product.carbs) * (serving.product_amount / 100)
        day = meal.creation_date.date().isoformat()

        if(day not in meals_total_per_day.keys()):
            meals_total_per_day[day] = []
        meals_total_per_day[day].append(meal_calories)
    
    
    calories_per_day = []
    for day, values in sorted(meals_total_per_day.items()):
        calories_per_day.append({
            "day": day,
            "total_calories": sum(values)
        })

    return calories_per_day

@meals_router.get("/chart/year")
def get_weightings_with_calories_year_info(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    def get_week_start(date: datetime) -> datetime:
        return date - timedelta(days=date.weekday())

    end = datetime.today()
    start = end - timedelta(days=365)

    meals = db.query(models.Meal).filter(
        models.Meal.user_id == current_user.id,
        models.Meal.creation_date >= start,
        models.Meal.creation_date <= end
    ).all()


    meals_total_per_day = dict()
    for meal in meals:
        meal_calories = 0
        for serving in meal.servings:
            if serving.product:
                product: models.Product = serving.product
                meal_calories += (4 * product.proteins + 9 * product.fats + 4 * product.carbs) * (serving.product_amount / 100)
        day = meal.creation_date.date().isoformat()

        if(day not in meals_total_per_day.keys()):
            meals_total_per_day[day] = []
        meals_total_per_day[day].append(meal_calories)
    
    
    avg_calories_per_day = dict()
    for day, values in sorted(meals_total_per_day.items()):

        week_start = get_week_start(datetime.fromisoformat(day)).date().isoformat()
        if(week_start not in avg_calories_per_day.keys()):
            avg_calories_per_day[week_start] = []
        avg_calories_per_day[week_start].append(sum(values))

    
    avg_calories_per_week = []
    for week_start, avg_calories in sorted(avg_calories_per_day.items()):
        avg = round(sum(avg_calories) / len(avg_calories), 2)
        
        avg_calories_per_week.append({
            "week_start": week_start,
            "average_calories": avg
        })
    
    return avg_calories_per_week

@meals_router.post("", response_model=schemas.MealBase)
def add_meal(meal: str = Form(...), image: UploadFile = File(None), current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    data_dict = json.loads(meal)
    meal_create = schemas.MealCreate(**data_dict)

    image_path = None
    if image and image.filename:
        paths = utils.save_image(image)
        image_path = paths

    db_item = models.Meal(
        user_id = current_user.id,
        meal_type_id = meal_create.meal_type_id,
        picture = image_path,
        creation_date = func.now()
    )

    db.add(db_item)
    db.commit()
    db.refresh(db_item)


    return db_item

@meals_router.put("/{meal_id}", response_model=bool)
def update_meal(meal_id: int, meal: str = Form(...), image: UploadFile = File(None), current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    if(not current_user):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Вы не авторизованы!"
        )
    
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
    
    data_dict = json.loads(meal)
    meal_create = schemas.MealCreate(**data_dict)

    image_path = None
    if image and image.filename:
        paths = utils.save_image(image)
        image_path = paths
    
    db_item.meal_type_id = meal_create.meal_type_id
    db_item.picture = image_path

    db.commit()
    db.refresh(db_item)

    return True

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