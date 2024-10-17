import google.generativeai as genai
import google.ai.generativelanguage as glm
from google.oauth2 import service_account
from dotenv import load_dotenv
import os


load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")



genai.configure(api_key=GEMINI_API_KEY)

def chat_session():
    #start a new session 
    #while recieving messages
    #   RAG from pinecone
    #   generate answer with langchain
    return