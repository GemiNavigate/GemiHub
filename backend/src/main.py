from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, constr
from typing import List, Optional
from datetime import datetime
import logfire
    
class Filter(BaseModel):
    min_lat: float = Field(..., ge=-90.0, le=90.0)
    max_lat: float = Field(..., ge=-90.0, le=90.0)
    min_lng: float = Field(..., ge=-180.0, le=180.0)
    max_lng: float = Field(..., ge=-180.0, le=180.0)
    cur_time: datetime
    time_range: int = 60 # In minute


class Reference(BaseModel):
    info: str
    lat: float = Field(..., ge=-90.0, le=90.0)
    lng: float = Field(..., ge=-180.0, le=180.0)
    time: datetime

class MetaData(BaseModel):
    lat: float = Field(..., ge=-90.0, le=90.0)
    lng: float = Field(..., ge=-180.0, le=180.0)
    time: datetime

class AskRequest(BaseModel):
    content: str
    cur_lat: float = Field(..., ge=-90.0, le=90.0)
    cur_lng: float = Field(..., ge=-180.0, le=180.0)
    filter: Filter


class AskResponse(BaseModel):
    response: str
    references: List[Reference] = None


class ShareRequest(BaseModel):
    content: str
    metadata: MetaData


class ShareResponse(BaseModel):
    status: str 


########## API ###########

app = FastAPI(root_path="/api")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "OK"}

@app.post("/ask")
async def ask(ask_request: AskRequest) -> AskResponse:
    response = AskResponse(
        response="Hello",
        references=[
            Reference(
                info="test",
                lat=25.0330,
                lng=121.5654,
                time="2024-10-19 10:05:44"
            )
        ]
    )
    return response

@app.post("/share")
async def share(share_request: ShareRequest) -> ShareResponse:
    response = ShareResponse(
        status="OK"
    )
    return response 
