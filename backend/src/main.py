from fastapi import FastAPI

app = FastAPI()

@app.get('/share_info')
def send_to_DB():
    return

@app.get('/ask_gemini')
def ask_gemini():
    return