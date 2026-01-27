from fastapi import FastAPI
import uvicorn

from models import Base
from database import engine
from routes import *


Base.metadata.create_all(bind=engine)
app = FastAPI()

app.include_router(auth_router)
app.include_router(weightings_router)
app.include_router(meals_router)
app.include_router(products_router)
app.include_router(servings_router)
app.include_router(users_router)



if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)