import google.generativeai as genai
import google.ai.generativelanguage as glm
from google.oauth2 import service_account
from dotenv import load_dotenv
import os


load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
SERVICE_ACCOUNT_FILE = os.getenv("SERVICE_ACCOUNT_FILE")
credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE)
scoped_credentials = credentials.with_scopes(
    ['https://www.googleapis.com/auth/cloud-platform', 'https://www.googleapis.com/auth/generative-language.retriever'])
generative_service_client = glm.GenerativeServiceClient(credentials=scoped_credentials)
retriever_service_client = glm.RetrieverServiceClient(credentials=scoped_credentials)
permission_service_client = glm.PermissionServiceClient(credentials=scoped_credentials)


genai.configure(api_key=GEMINI_API_KEY)

def chat_session():
    #start a new session 
    #while recieving messages
    #   RAG from pinecone
    #   generate answer with langchain
    return