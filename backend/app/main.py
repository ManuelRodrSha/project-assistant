import time

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from app.api.routes import router
from app.core.config import settings
from app.db.models import Base
from app.db.session import engine

app = FastAPI(title=settings.APP_NAME)

origins = [origin.strip() for origin in settings.CORS_ORIGINS.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def wait_for_db(max_retries=20, delay=2):
    for attempt in range(1, max_retries + 1):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print("DB connection OK")
            return
        except Exception as e:
            print(f"DB not ready yet ({attempt}/{max_retries}): {e}")
            if attempt == max_retries:
                raise
            time.sleep(delay)


@app.on_event("startup")
def on_startup():
    wait_for_db()
    Base.metadata.create_all(bind=engine)
    print("Tables ready")


@app.get("/")
def root():
    return {"message": "backend alive"}


@app.get("/health")
def health():
    return {"status": "healthy"}


app.include_router(router)