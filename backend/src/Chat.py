import google.generativeai as genai
import google.ai.generativelanguage as glm
from google.oauth2 import service_account
from dotenv import load_dotenv
from Corpus import CorpusAgent
from typing import Dict
import json
from jsonschema import validate
from mapAPI import MapHandler
import uuid
from datetime import datetime
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
        genai.configure(api_key=GEMINI_API_KEY)
        self.map_handler = MapHandler()
        generation_config = {
            "temperature": 0.5,
            # "top_p": 0.95,
            # "top_k": 64,
            # "max_output_tokens": 8192,
            # "response_mime_type": "plain/text",
        }
        
        self.filter_format = {
            "location": {
                "dst": ""
            },
            "timestamp": {
                "current_time": "",
                "range": 60
            }
        }
        # but if the time user specify is not in the interval [current_time-60min, current_time],
        # fill this column with "invalid_time".
                                    
        
        self.model = genai.GenerativeModel(
            model_name="gemini-1.5-pro",
            generation_config=generation_config,
            system_instruction=f'''
            when receiving a request, check the following things step by step,
            1. if user is asking about things happening around a place,
                - contain four key:values in your response.parts, and return in json format 
                    1. use_function_call: just fill this column with 1
                    2. text: return a string which is the text sent from the user to the letter.
                    3. filter: this require a json format, make sure you follow the provided format: {self.filter_format}.
                        - mind that dst in this format is float, which means the distance around that place the user want, 
                            if user doesn't specify, use 5.0 instead.
                        - and  current_time in this format str, if user specify the time in the request, use that time.
                            if the time the user give is not accurate time, change it into int. for example: 5 minute ago -> -5
                            else, fill this column with "current_time"
                    4. place: the place where user want information. if user doesn't specify the place, fill this column with "current_place"
                - to specify the meaning of "things" in "things happening around a place":
                    for example, raining, crowds, emergencies.
            2. else, contain two key:values in your response.parts, and return in json format,
                1. use_function_call: 0
                2. text: response generated on your own based on user request.
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
        
        # convert response into json format
        response = response.text.strip("```json\n").rstrip(' ').rstrip('`')
        json_data = json.loads(response)
        try:
            validate(instance=json_data, schema=self.filter_format)
        except Exception as e:
            print("invalid json format", e)
        json_dump = json.dumps(json_data["parts"][0], indent=4)
        print(json_dump)
        print("type of json dump", type(json_dump))
        json_dump = json.loads(json_dump)
        self.validate_response(json_dump)
        
        return json_data
       
    def validate_response(self, response: Dict):
        # call gen_answer
        print("type of response", type(response))
        if response["use_function_call"] == True:
            filter = response["filter"]
            if self.map_handler.get_coor(response["place"]) != None:
                filter["location"]["lat"], filter["location"]["lng"] = self.map_handler.get_coor(response["place"])
            if filter["timestamp"]["current_time"] == "current_time":
                filter["timestamp"]["current_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print("this is filter")
            filter = json.dumps(filter, indent=4)
            print(filter)
        # return text
        else:
            text = response["text"]
            
    
    def gen_answer(self, filters: Dict[str, Dict], query: str) -> Dict:
        self.corpus.generate_answer(filters=filters, query=query, answer_style="VERBOSE")
     
        
if __name__ == "__main__":
    chat_handler = ChatHandler()
    request = "is it raining in Chiao Tung University 15 minute ago?"
    # request = "hello, what is your name"
    session = chat_handler.create_chat_session()
    response = chat_handler.get_response(session, request)
    print("response!!!")
    # print(response)
    response = json.dumps(response["parts"])
    print(response)

