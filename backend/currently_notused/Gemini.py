import google.generativeai as genai
import google.ai.generativelanguage as glm
from google.oauth2 import service_account
from dotenv import load_dotenv
from Corpus import CorpusAgent
from typing import Dict
import requests
from vertexai.generative_models import(
    Content,
    FunctionDeclaration,
    GenerativeModel,
    Part,
    Tool,
)
import uuid
import os

# set keys
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
SERVICE_ACCOUNT_FILE = os.getenv("SERVICE_ACCOUNT_FILE")
CORPUS_NAME=os.getenv("CORPUS_NAME")

class ChatHandler():
    def __init__(self):
        corpus_document = "corpora/gemihubcorpus-vviogw42kc9t/documents/test-document-3-hknhyc3kwtsx"
        self.corpus = CorpusAgent(document=corpus_document)
        # genai.configure(api_key=GEMINI_API_KEY)
        self.model = GenerativeModel("gemini-1.5-flash")
        self.filter_format = '''{
            "location": {
                "lat": {
                    "type": "float", 
                    "description": "latitude of the place user is asking"
                },
                "lng": {
                    "type": "float", 
                    "description": "longitude of the place user is asking"
                },
                "dst": {
                    "type": "float",
                    "description": ''''''destination around that place the user want, 
                                    if user doesn't specify, use 5.0 instead.''''''
                }
            },
            "timestamp": {
                "current_time": {
                    "type": "str",
                    "description": ''''''if user specify the time in the request, use that time.
                                    but if the time user specify is not in the interval [current_time-60min, current_time],
                                    fill this column with "invalid time".
                                    else, use the current time in Taiwan,
                                    make sure you follow the format: %Y-%m-%d %H:%M:%S''''''
                        },
                "range": 60
            }
        }'''
        
        self.functions = FunctionDeclaration(
            name = "gen_answer",
            description = "generate the response using RAG",            
            parameters = {
                "type": "object",
                "properties": {
                    "filter": {
                        "type": "object",
                        "description": f"generate answer following the format: {self.filter_format}, make sure all the parameter are correct.",
                    },
                    "query": {
                        "type": "string",
                        "description": "fill the request sent from the user to the letter"
                    }
                },
                "required": ["filter", "query"],
            }
        )
        self.tool = Tool(
            function_declarations=[self.functions]
        )
        
    def create_chat_session(self):
        # start a new session and return session id 
        chat_session = self.model.start_chat(history=[])
        session_id = str(uuid.uuid4())
        self.chat_sessions[session_id] = chat_session
        
        return session_id

    def delete_chat_session(self, session_id):
        del self.chat_sessions[session_id]
        return f"seccussfully delete the session: {session_id}"
    
    def get_response(self, text):
        # while recieving messages
        #  RAG from corpus
        # chat_session = self.chat_sessions[session_id]
        # response = chat_session.send_message(text)
        response = self.model.generate_content(text, tools=[self.tool])
        return response
    
    def gen_answer(self, filters: Dict[str, Dict], query: str) -> Dict:
        self.corpus.generate_answer(filters=filters, query=query, answer_style="VERBOSE")
        
    def call_func_in_response(self, response):
        for part in response.parts:
            print("parts: ", part.text)
            
            if fn := part.function_call:
                args=", ".join(f"{key}={val}" for key, val in fn.args.items())

if __name__ == "__main__":
    chat_handler = ChatHandler()
    request = "is it raining in Chaung Tung University?"
    # session = chat_handler.create_chat_session()
    response = chat_handler.get_response(request)
    print(response)