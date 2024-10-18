from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, constr
from typing import List, Optional
from datetime import datetime
import logfire

from Chat import ChatHandler

app = FastAPI()
    
class Filter(BaseModel):
    min_lat: float = Field(..., ge=-90.0, le=90.0)
    max_lat: float = Field(..., ge=-90.0, le=90.0)
    min_lng: float = Field(..., ge=-180.0, le=180.0)
    max_lng: float = Field(..., ge=-180.0, le=180.0)
    current_time: datetime
    time_range: int = 60 # In minute

class Reference(BaseModel):
    messaege: str
    lat: float = Field(..., ge=-90.0, le=90.0)
    lng: float = Field(..., ge=-180.0, le=180.0)
    time: datetime

class AskMessage(BaseModel):
    query: str
    filter: Filter

class AskResponse(BaseModel):
    response: str
    reference: List[Reference]

class ShareMessage(BaseModel):
    #  


class ShareResponse(BaseModel):
    # 





########## API ###########

@app.post("/ask")
async def ask(ask_message: AskMessage):
    return {"message":"OK"}

@app.get("/")
async def root():
    return {"message": "OK"}

