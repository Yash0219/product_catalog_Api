from fastapi import FastAPI
from database import engine , Base

app = FastAPI(title="product_catalog_api")

Base.metadata.create_all(bind = engine)

@app.get("/")
def get_root():
    return{"status":"online",
           "message":"welcome!"}