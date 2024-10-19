from fastapi import FastAPI
from Corpus import CorpusAgent
from backend.src.Chat_new import ChatAgent

app = FastAPI()

@app.get('/share_info')
def send_to_DB():
    return

@app.get('/ask_gemini')
def ask_gemini():
    return