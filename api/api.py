import os
from contextlib import asynccontextmanager
from typing import List

from dotenv import load_dotenv
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from api.handlers import get_comps_handler, get_champions_handler, get_items_handler
from common.db import DB
from common.models import Champion, Comp, CompositeItem

load_dotenv()


@asynccontextmanager
async def lifespan(_: FastAPI):
    # This function is called when the app starts up
    db.connect()
    yield
    # And yields after the app begins shutting down
    db.disconnect()


class ChampionResponse(Champion):
    pass


class CompResponse(Comp):
    pass


class ItemResponse(CompositeItem):
    pass


db = DB()
app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("CORS_SPA_ORIGIN", "http://localhost:8080")],
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"msg": "TFT Suggester API"}


@app.get("/comps", response_model=List[CompResponse])
async def get_comps():
    return get_comps_handler(db.get_comps_collection())


@app.get("/champions", response_model=List[ChampionResponse])
async def get_champions():
    return get_champions_handler(db.get_champions_collection())


@app.get("/items", response_model=List[ItemResponse])
async def get_items():
    return get_items_handler(db.get_items_collection())
