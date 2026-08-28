from fastapi import FastAPI
from sqlalchemy import text

app = FastAPI()

@app.get("/")
def home():
    return {"message": "FastAPI fonctionne"}