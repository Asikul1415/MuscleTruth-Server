from datetime import datetime

from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, Table, LargeBinary
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from argon2 import PasswordHasher

from database import Base


SALT = 'YOUR_SALT'.encode('utf-8')


Base = declarative_base()
ph = PasswordHasher()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    password = Column(String(255), nullable=False)
    age = Column(Integer, nullable=False)
    profile_picture = Column(LargeBinary)

    weightings = relationship('Weighting', back_populates='user')
    meals = relationship('Meal', back_populates='user')
    products = relationship('Product', back_populates='user')

    def verify_password(self, password: str) -> bool:
        try:
            return ph.verify(self.password, password)
        except:
            return False

    @staticmethod
    def get_password_hash(password: str) -> str:
        return ph.hash(password, salt=SALT)

class Weighting(Base):
    __tablename__ = "weightings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    result = Column(Numeric(6, 2), nullable=False)
    picture = Column(LargeBinary)
    creation_date = Column(DateTime(timezone=True), default=datetime.astimezone(datetime.now()), nullable=False)

    user = relationship('User', back_populates='weightings')

class Meal(Base):
    __tablename__ = "meals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    picture = Column(LargeBinary)
    creation_date = Column(DateTime(timezone=True), default=datetime.astimezone(datetime.now()), nullable=False)

    user = relationship('User', back_populates='meals')
    servings = relationship('Serving', back_populates='meal')

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    title = Column(String(255), nullable=False)
    proteins = Column(Integer, nullable=False)
    fats = Column(Integer, nullable=False)
    carbs = Column(Integer, nullable=False)
    picture = Column(LargeBinary)

    user = relationship('User', back_populates='products')
    servings = relationship('Serving', back_populates='product')

class Serving(Base):
    __tablename__ = "servings"

    id = Column(Integer, primary_key=True, index=True)
    meal_id = Column('meal_id', Integer, ForeignKey('meals.id'))
    product_id = Column('product_id', Integer, ForeignKey('products.id'))
    product_amount =  Column('product_amount', Numeric(6, 2), nullable=False)

    meal = relationship('Meal', back_populates='servings')
    product = relationship('Product', back_populates='servings')