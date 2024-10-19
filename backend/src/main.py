from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, constr
from typing import List, Optional
from datetime import datetime
import logfire
    
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


class ClientShareData(BaseModel):
    test: str


class ServerShareData(BaseModel):
    test: str


class AskMessage(BaseModel):
    query: str
    filter: Filter


class AskResponse(BaseModel):
    response: str
    reference: List[Reference] = None


class ShareMessage(BaseModel):
    content: str
    image: any
    metadata: 


class ShareResponse(BaseModel):
    tmp: str
    # 

    


########## API ###########

app = FastAPI(root_path="/api")

@app.get("/")
async def root():
    return {"message": "OK"}

@app.post("/ask")
async def ask(ask_message: AskMessage) -> AskResponse:
    response = AskResponse(
        response="Hello",
        reference=[
            Reference(
                messaege="test",
                lat=25.0330,
                lng=121.5654,
                time="2024-10-19 10:05:44"
            )
        ]
    )
    return response

@app.post("/share")
async def share(share_message: ShareMessage) -> ShareResponse:
    return {"message":"OK"}
