# app/main.py
from fastapi import FastAPI
from app.routes import router as message_router
from app.config import configure_cors

app = FastAPI()

configure_cors(app)

app.include_router(message_router)
