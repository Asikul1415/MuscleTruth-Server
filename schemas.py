from datetime import datetime
from typing import Optional, List, Any

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from models import Product


#BASIS CLASSES
class UserBase(BaseModel):
    id: Optional[int] = None
    name: str = Field(..., max_length=255)
    email: EmailStr = Field(..., max_length=255)
    password: str = Field(..., max_length=255)
    age: int = Field(..., ge=0, le=150)
    profile_picture: Optional[bytes] = None

class WeightingBase(BaseModel):
    id: Optional[int] = None
    user_id: int = Field(...)
    result: float = Field(..., ge=0, le=999.99)
    picture: Optional[bytes] = None
    creation_date: Optional[datetime] = datetime.now()

class MealBase(BaseModel):
    id: Optional[int] = None
    user_id: int = Field(...)
    picture: Optional[bytes] = None
    creation_date: Optional[datetime] = None

class ProductBase(BaseModel):
    id: Optional[int] = None
    title: str = Field(..., max_length=255)
    user_id: int = Field(...)
    proteins: int = Field(..., ge=0)
    fats: int = Field(..., ge=0)
    carbs: int = Field(..., ge=0)
    picture: Optional[bytes] = None

class ServingBase(BaseModel):
    id: Optional[int] = None
    meal_id: int = Field(...)
    product_id: int = Field(...)
    product_amount: float = Field(..., ge=0, le=999.99)

class Token(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    user_id: int

#QUERIES
class UserLogin(BaseModel):
    email: EmailStr = Field(..., max_length=255)
    password: str = Field(..., max_length=255)

class WeightingCreate(BaseModel):
    result: float = Field(..., ge=0, le=999.99)
    picture: Optional[bytes] = None
    creation_date: Optional[datetime] = datetime.now()

class WeightingUpdate(BaseModel):
    result: float = Field(..., ge=0, le=999.99)
    picture: Optional[bytes] = None
    
class MealCreate(BaseModel):
    picture: Optional[bytes] = None
    creation_date: Optional[datetime] = None

class MealUpdate(BaseModel):
    picture: Optional[bytes] = None

class ProductCreate(BaseModel):
    title: str = Field(..., max_length=255)
    proteins: int = Field(..., ge=0)
    fats: int = Field(..., ge=0)
    carbs: int = Field(..., ge=0)
    picture: Optional[bytes] = None

class ServingCreate(BaseModel):
    product_id: int = Field(...)
    product_amount: float = Field(..., ge=0, le=999.99)

#QUERIES RESPONSES
class AddResponse(BaseModel):
    id: int