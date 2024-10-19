from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, constr, HttpUrl
from typing import List, Optional, Union
from datetime import datetime
from dotenv import load_dotenv
import os
import logfire

import google.ai.generativelanguage as glm
from google.oauth2 import service_account

from PhotoModel import PhotoModel
from Corpus import CorpusAgent
from Chat import ChatAgent
    

class Filter(BaseModel):
    min_lat: float = Field(..., ge=-90.0, le=90.0)
    max_lat: float = Field(..., ge=-90.0, le=90.0)
    min_lng: float = Field(..., ge=-180.0, le=180.0)
    max_lng: float = Field(..., ge=-180.0, le=180.0)
    cur_time: datetime
    time_range: int = 60  # In minutes


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
    content: str = Field(..., description="User-provided text related to the image.")
    uri: Optional[HttpUrl] = Field(..., description="URL of the uploaded image.")
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
    try:
        ask_request.filter.cur_time = ask_request.filter.cur_time.strftime("%Y-%m-%d %H:%M:%S")
        agent = ChatAgent()
        print("ask: ", ask_request.content)
        answer, references = agent.chat(
            message=ask_request.content,
            filters=ask_request.filter.dict(),
            current_lat=ask_request.cur_lat,
            current_lng=ask_request.cur_lng,
        )
        print(answer, references);
        response = AskResponse(
            response=answer,
            references=[
                Reference(
                    info=ref["info"],
                    lat=ref["lat"],
                    lng=ref["lng"],
                    time=datetime.fromtimestamp(ref["time"]),
                ) for ref in (references or [])  # Handle case where references are None
            ]
        )
        return response

    except Exception as e:
        print(f"Error occurred in ask(): {e}")
        raise HTTPException(
            status_code=500, 
            detail="Internal server error. Please try again later."
        )



@app.post("/share")
async def share(share_request: ShareRequest) -> ShareResponse:
    try:
        print("share: ", share_request.content)
        photo_model = PhotoModel()
        result = photo_model.analyze_image(share_request.uri, share_request.content)
        load_dotenv()
        DEV_DOC = os.getenv("TEST_DOCUMENT")
        agent = CorpusAgent(document=DEV_DOC)
        agent.add_info_to_document(
            content=result,
            lat=share_request.metadata.lat,
            lng=share_request.metadata.lng,
            time=share_request.metadata.time.strftime("%Y-%m-%d %H:%M:%S")
        )

        return ShareResponse(status="OK")

    except Exception as e:
        print(f"Error occurred in share(): {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error. Please try again later."
        )
'''
@app.post("/share")
async def share(share_request: ShareRequest) -> ShareResponse:
    try:
        load_dotenv()
        DEV_DOC=os.getenv("TEST_DOCUMENT")
        agent = CorpusAgent(document=DEV_DOC)
        print("share: ", share_request.content)
        agent.add_info_to_document(
            content=share_request.content, 
            lat=share_request.metadata.lat, 
            lng=share_request.metadata.lng, 
            time=share_request.metadata.time.strftime("%Y-%m-%d %H:%M:%S")
        )
        response = ShareResponse(
            status="OK"
        )
        return response

    except Exception as e:
        print(f"Error occurred in share(): {e}")
        raise HTTPException(
            status_code=500, 
            detail="Internal server error. Please try again later."
        )
'''
