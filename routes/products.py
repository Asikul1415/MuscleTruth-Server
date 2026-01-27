from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

import models, schemas
from database import get_db
from login import (
    get_current_user,
)



products_router = APIRouter(prefix='/api/products')


@products_router.get("", response_model=List[schemas.ProductBase])
def get_products(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_items = db.query(models.Product).all()

    return db_items

@products_router.get("/{product_id}", response_model=schemas.ProductBase)
def get_product(product_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_item = db.query(models.Product).filter(models.Product.id == product_id).first()
    if(not db_item):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Такого продукта не существует!",
        )
    
    return db_item

@products_router.post("", response_model=schemas.AddResponse)
def add_product(product: schemas.ProductCreate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
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

@products_router.put("/{product_id}", response_model=schemas.AddResponse)
def update_product(product: schemas.ProductCreate, product_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_item = db.query(models.Product).filter(models.Product.id == product_id).first()
    if(not db_item):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Такого продукта не существует!",
        )
    elif(db_item.user_id != current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Продукт может редактировать только пользователь, создавший его!",
        )
    
    db_item.title = product.title
    db_item.proteins = product.proteins
    db_item.fats = product.fats
    db_item.carbs = product.carbs
    db_item.picture = product.picture

    db.commit()
    db.refresh(db_item)

    return db_item

@products_router.delete("/{product_id}", response_model=schemas.AddResponse)
def delete_product(product_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_item = db.query(models.Product).filter(models.Product.id == product_id).first()
    if(not db_item):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Такого продукта не существует!",
        )
    elif(db_item.user_id != current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Продукт может удалить только пользователь, создавший его!",
        )
    
    db.delete(db_item)
    db.commit()

    return db_item