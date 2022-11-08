import os
from typing import List

from dotenv import load_dotenv
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from api.handlers import get_comps_handler, get_champions_handler, get_items_handler
from cdragon.items import Item as CDragonItem
from common.db import DB
from common.models import Champion, Comp

load_dotenv()
app = FastAPI()
db = DB()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("CORS_SPA_ORIGIN", "http://localhost:8080")],
    allow_methods=["GET"],
    allow_headers=["*"],
)


class ChampionResponse(Champion):
    pass


class CompResponse(Comp):
    pass


class ItemResponse(CDragonItem):
    pass


@app.on_event("startup")
async def startup():
    db.connect()


@app.on_event("shutdown")
async def shutdown():
    db.disconnect()


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
    return get_items_handler()
