from sqlalchemy import Column, Integer, String, Numeric, DateTime, Time, ForeignKey, Table, LargeBinary
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    password = Column(String(255), nullable=False)
    age = Column(Integer, nullable=False)
    profile_picture = Column(LargeBinary)

    meals = relationship('Meal', back_populates='user')
    weightings = relationship('Weighting', back_populates='user')

class Weighting(Base):
    __tablename__ = "weightings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    result = Column(Numeric(6, 2), nullable=False)
    picture = Column(LargeBinary)
    creation_date = Column(DateTime(timezone=True), default=datetime.utcnow(), nullable=False)

    user = relationship('User', back_populates='weightings')

meals_products = Table(
    'meals_products',
    Base.metadata,
    Column('meal_id', Integer, ForeignKey('meals.id'), primary_key=True),
    Column('product_id', Integer, ForeignKey('products.id'), primary_key=True),
    Column('product_amount', Numeric(6, 2), nullable=False)
)

class Meal(Base):
    __tablename__ = "meals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    picture = Column(LargeBinary)
    creation_date = Column(DateTime(timezone=True), default=datetime.utcnow(), nullable=False)

    user = relationship('User', back_populates='meals')
    meals = relationship('User', back_populates='meals')
    products = relationship('Product', secondary=meals_products, back_populates='meals')

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    proteins = Column(Integer, nullable=False)
    fats = Column(Integer, nullable=False)
    carbs = Column(Integer, nullable=False)
    picture = Column(LargeBinary)

    meals = relationship('Meal', secondary=meals_products, back_populates='products')