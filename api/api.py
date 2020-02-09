from typing import List

from fastapi import FastAPI
from pydantic import BaseModel

from api.handlers import get_comps_handler, get_champions_handler
from common.db import DB

app = FastAPI()


class ChampionResponse(BaseModel):
    name: str
    image: str


class CompResponse(BaseModel):
    name: str
    tier: str
    champions: List[ChampionResponse]


@app.on_event("startup")
async def startup():
    DB.connect()


@app.on_event("shutdown")
async def shutdown():
    DB.disconnect()


@app.get('/')
def root():
    return {'msg': 'TFT Suggester API'}


@app.get('/comps', response_model=List[CompResponse])
async def get_comps():
    return get_comps_handler(DB.get_instance().get_comps_collection())


@app.get('/champions', response_model=List[ChampionResponse])
async def get_champions():
    return get_champions_handler(DB.get_instance().get_champions_collection())
