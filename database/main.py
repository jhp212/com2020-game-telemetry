from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from database.database import engine, SessionLocal # type: ignore
from database.models import Base, Parameters, Users # type: ignore
from database.security import get_password_hash
from database.constants import DEFAULT_PARAMETERS, DEFAULT_USERS

from database.routers import auth, users, game_data

# Create DB Tables
Base.metadata.create_all(bind=engine)

# Setup Defaults
def initialize_db_defaults():
    db = SessionLocal()
    try:
        for param in DEFAULT_PARAMETERS:
            if not db.query(Parameters).filter(Parameters.name == param["name"]).first():
                db.add(Parameters(name=param["name"], value=param["value"]))
        for user in DEFAULT_USERS:
            if not db.query(Users).filter(Users.username == user["username"]).first():
                db.add(Users(username=user["username"], password_hash=get_password_hash(user["password"]), is_admin=user["is_admin"]))
        db.commit()
    finally:
        db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_db_defaults()
    yield

app = FastAPI(lifespan=lifespan, title="Game Telemetry API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connect all the split files to the main app
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(game_data.router)