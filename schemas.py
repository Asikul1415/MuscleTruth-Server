from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, ConfigDict, EmailStr, Field



#BASIS CLASSES
class UserBase(BaseModel):
    id: Optional[int] = None
    name: str = Field(..., max_length=255)
    email: EmailStr = Field(..., max_length=255)
    password: str = Field(..., max_length=255)
    age: int = Field(..., ge=0, le=150)
    profile_picture: Optional[str] = None

class WeightingBase(BaseModel):
    id: Optional[int] = None
    user_id: int = Field(...)
    result: float = Field(..., ge=0, le=999.99)
    picture: Optional[str] = None
    creation_date: Optional[datetime] = datetime.now()

class MealBase(BaseModel):
    id: Optional[int] = None
    user_id: int = Field(...)
    meal_type_id: int = Field(...)
    picture: Optional[str] = None
    creation_date: Optional[datetime] = None
    products: Optional[List[ProductBase]] = None

class SavedMeal(BaseModel):
    id: Optional[int] = None
    title: str = Field(..., max_length=255)
    meal_id: int = Field(...)
    user_id: int = Field(...)

class ProductBase(BaseModel):
    id: Optional[int] = None
    title: str = Field(..., max_length=255)
    user_id: int = Field(...)
    proteins: int = Field(..., ge=0)
    fats: int = Field(..., ge=0)
    carbs: int = Field(..., ge=0)
    picture: Optional[str] = None

class FavouriteProduct(BaseModel):
    id: Optional[int] = None
    product_id: int = Field(...)
    user_id: int = Field(...)

class RecentServing(BaseModel):
    id: Optional[int] = None
    serving_id: int = Field(...)
    user_id: int = Field(...)
    use_date: datetime

class ServingBase(BaseModel):
    id: Optional[int] = None
    meal_id: int = Field(...)
    product_id: int = Field(...)
    product_amount: float = Field(..., ge=0, le=9999.99)

class Token(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    user_id: int

#QUERIES
class UserLogin(BaseModel):
    email: EmailStr = Field(..., max_length=255)
    password: str = Field(..., max_length=255)

class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    email: Optional[EmailStr] = Field(None, max_length=255)
    password: Optional[str] = Field(None, max_length=255)
    age: Optional[int] = Field(None, ge=0, le=150)
    profile_picture: Optional[str] = None

class WeightingsRequest(BaseModel):
    start_date: Optional[str] = None
    end_date: Optional[str] = None

class WeightingCreate(BaseModel):
    result: float = Field(..., ge=0, le=999.99)
    picture: Optional[str] = None
    creation_date: Optional[datetime] = None

class WeightingUpdate(BaseModel):
    result: float = Field(..., ge=0, le=999.99)
    picture: Optional[str] = None

class MealTypeTotal(BaseModel):
    proteins: float = Field(..., ge=0)
    fats: float = Field(..., ge=0)
    carbs: float = Field(..., ge=0)
    total_calories: float = Field(..., ge=0, le=9999.99)
class MealCreate(BaseModel):
    meal_type_id: int = Field(...)
    picture: Optional[str] = None
    creation_date: Optional[datetime] = datetime.now()

class ProductCreate(BaseModel):
    title: str = Field(..., max_length=255)
    proteins: int = Field(..., ge=0)
    fats: int = Field(..., ge=0)
    carbs: int = Field(..., ge=0)
    picture: Optional[str] = None

class ServingCreate(BaseModel):
    product_id: int = Field(...)
    product_amount: float = Field(..., ge=0, le=9999.99)

#QUERIES RESPONSES
class AddResponse(BaseModel):
    id: int