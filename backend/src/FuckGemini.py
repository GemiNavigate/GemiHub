import google.generativeai as genai
import google.ai.generativelanguage as glm
from google.oauth2 import service_account
from dotenv import load_dotenv
from Corpus import CorpusAgent
from typing import Dict
from google.cloud import aiplatform
import uuid
import os

# set keys
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
SERVICE_ACCOUNT_FILE = os.getenv("SERVICE_ACCOUNT_FILE")
CORPUS_NAME=os.getenv("CORPUS_NAME")


def gen_answer(self, filters: Dict[str, Dict], query: str) -> Dict:
        corpus_document = "corpora/gemihubcorpus-vviogw42kc9t/documents/test-document-3-hknhyc3kwtsx"
        corpus = CorpusAgent(document=corpus_document)
        '''
        "function description": "generate the response using RAG",
        "parameters":
            query (str): use the request user send
            filter (object): please follow the given format:
                "filter": {
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
                    },
                },
        reutrns:
            Dict: json response
        '''
        response = corpus.generate_answer(filters=filters, query=query, answer_style="VERBOSE")
        return response
class ChatHandler():
    def __init__(self):
        corpus_document = "corpora/gemihubcorpus-vviogw42kc9t/documents/test-document-3-hknhyc3kwtsx"
        self.corpus = CorpusAgent(document=corpus_document)
        genai.configure(api_key=GEMINI_API_KEY)
        generation_config = {
            "temperature": 0.0,
            # "top_p": 0.95,
            # "top_k": 64,
            # "max_output_tokens": 8192,
            # "response_mime_type": "text/plain",
        }
        
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
        
        response_tool = {
            "name": "gen_answer",
            "description": "generate the response using RAG",
            "parameters": {
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
        }
        
        # tool = [response_tool]
        # tool = [self.gen_answer]
        self.model = genai.GenerativeModel(
            model_name="gemini-1.5-pro",
            generation_config=generation_config,
            tools=[gen_answer],
            system_instruction=f'''
            when receiving a request, check the following things step by step,
            1. if user is asking about things happening around a place, 
                then call function "gen_response" and generate required parameter.
                - to specify the meaning of "things" in "things happening around a place":
                    for example, raining, crowds, emergencies.
                - when calling gen_response, if needed arguments are missing, tell me what your already know and ask for information
                1. make sure filter is passed to function with type Dict[str, Dict], the format is {self.filter_format}
                2. make sure query is passed to function with type str, fill this column use the text sent from the user to the letter.
            2. else, return a json object, call function "no_function_call", 
                pass the arg text, which is the response generated on your own based on user request.
            '''
        )
        
        self.chat_sessions = {}
              
    def create_chat_session(self):
        # start a new session and return session id 
        chat_session = self.model.start_chat(
            history=[]
        )
        session_id = str(uuid.uuid4())
        self.chat_sessions[session_id] = chat_session
        
        return session_id

    def delete_chat_session(self, session_id):
        del self.chat_sessions[session_id]
        return f"seccussfully delete the session: {session_id}"
    
    def get_response(self, session_id, text):
        # while recieving messages
        #  RAG from corpus
        chat_session = self.chat_sessions[session_id]
        response = chat_session.send_message(text)
        
        return response
    
    def gen_answer(self, filters: Dict[str, Dict], query: str) -> Dict:
        '''
        "function description": "generate the response using RAG",
        "parameters":
            query (str): use the request user send
            filter (object): please follow the given format:
                "filter": {
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
                    },
                },
        reutrns:
            Dict: json response
        '''
        self.corpus.generate_answer(filters=filters, query=query, answer_style="VERBOSE")
        
    def call_func_in_response(self, response):
        for part in response.parts:
            print("parts: ", part.text)
            
            if fn := part.function_call:
                args=", ".join(f"{key}={val}" for key, val in fn.args.items())

if __name__ == "__main__":
    chat_handler = ChatHandler()
    request = "is it raining in Chaung Tung University?"
    session = chat_handler.create_chat_session()
    response = chat_handler.get_response(session, request)
    print(response)