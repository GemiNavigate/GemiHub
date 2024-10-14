from fastapi import FastAPI
import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()
GEMINI_API_KEY=os.getenv("GEMINI_API_KEY")
PINECONE_API_KEY=os.getenv("PINECONE_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

app = FastAPI()

@app.get('/share_info')
def send_to_DB():
    return

@app.get('/ask_gemini')
def ask_gemini():
    return