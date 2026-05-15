from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

import models, schemas
from database import get_db
from login import (
    get_current_user,
)
import utils
import json


products_router = APIRouter(prefix='/api/products')


@products_router.get("", response_model=List[schemas.ProductBase])
def get_products(search_query: str = None, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_items = db.query(models.Product)

    if(search_query):
        print(search_query)
        db_items = db_items.filter(models.Product.title.ilike(f"%{search_query}%"))

    return db_items.all()

@products_router.get("/favourites", response_model=List[schemas.FavouriteProduct])
def get_favourite_products(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_items = db.query(models.FavouriteProduct).filter(models.FavouriteProduct.user_id == current_user.id)

    return db_items.all()

@products_router.get("/favourites/{product_id}", response_model=schemas.FavouriteProduct|None)
def get_favourite_product(product_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_item = db.query(models.FavouriteProduct).filter(models.FavouriteProduct.product_id == product_id).first()

    return db_item


@products_router.post("/favourites", response_model=schemas.FavouriteProduct)
def add_favourite_products(product_id: int = Form(...), current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_item = models.FavouriteProduct(
        product_id = product_id,
        user_id = current_user.id
    )
    
    db.add(db_item)
    db.commit()
    db.refresh(db_item)

    return db_item

@products_router.delete("/favourites/{product_id}", response_model=bool)
def delete_favourite_product(product_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_item = db.query(models.FavouriteProduct).filter(models.FavouriteProduct.product_id == product_id).first()
    if(db_item != None):
        db.delete(db_item)
        db.commit()
        return True
    return False

@products_router.get("/{product_id}", response_model=schemas.ProductBase)
def get_product(product_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_item = db.query(models.Product).filter(models.Product.id == product_id).first()
    if(not db_item):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Такого продукта не существует!",
        )
    
    return db_item

@products_router.post("", response_model=schemas.ProductBase)
def add_product(product: str = Form(...), image: UploadFile = File(None), current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    data_dict = json.loads(product)
    product_create = schemas.ProductCreate(**data_dict)

    image_path = None
    if image and image.filename:
        paths = utils.save_image(image)
        image_path = paths

    db_item = models.Product(
        user_id = current_user.id,
        title = product_create.title,
        proteins = product_create.proteins,
        fats = product_create.fats,
        carbs = product_create.carbs,
        picture = image_path,
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
