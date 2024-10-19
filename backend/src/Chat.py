import google.generativeai as genai
import google.ai.generativelanguage as glm
from google.oauth2 import service_account
from dotenv import load_dotenv
from Corpus import CorpusAgent
from typing import Dict
import json
from jsonschema import validate
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
        genai.configure(api_key=GEMINI_API_KEY)
        generation_config = {
            "temperature": 0.5,
            # "top_p": 0.95,
            # "top_k": 64,
            # "max_output_tokens": 8192,
            # "response_mime_type": "text/plain",
        }
        
        self.filter_format = {
            "location": {
                "dst": {
                    "type": "float",
                    "description": '''destination around that place the user want, 
                                    if user doesn't specify, use 5.0 instead.'''
                }
            },
            "timestamp": {
                "current_time": {
                    "type": "str",
                    "description": '''if user specify the time in the request, use that time.
                                    else, fill this column with "current_time"'''
                        },
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
                - contain three arguments in your response.parts
                    1. use_function_call: just fill this column with True
                    2. text: return a string which is the text sent from the user to the letter.
                    3. filter: this require a json format, make sure you follow the provided format: {self.filter_format}
                    4. place: the place where user want information. if user doesn't specify the place, fill this column with "current_place"
                - to specify the meaning of "things" in "things happening around a place":
                    for example, raining, crowds, emergencies.
            2. else, contain two arguments in your response.parts,
                1. use_function_call: False
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
    
<<<<<<< HEAD
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
        # print(response)
        # self.validate_response(response)
        
        
        return response    

       
    def validate_response(self, response: json):
        # call gen_answer
        if response["use_function_call"] == "True":
            filter = response
            filter["location"]["lat"] = 0
            filter["location"]["lng"] = 0
            
        # return text 
        else:
            text = response["text"]
            
    
    def gen_answer(self, filters: Dict[str, Dict], query: str) -> Dict:
        self.corpus.generate_answer(filters=filters, query=query, answer_style="VERBOSE")
     
        
if __name__ == "__main__":
    chat_handler = ChatHandler()
    request = "is it raining in Chaung Tung University at 4 p.m.?"
    # request = "hello, what is your name?"
    session = chat_handler.create_chat_session()
    response = chat_handler.get_response(session, request)
    # print(response)
=======
    def chat(self, message, filters):
        chat = self.model.start_chat()
        response = chat.send_message(message)

        for part in response.parts:
            if fn := part.function_call:
                args = ", ".join(f"{key}={val}" for key, val in fn.args.items())
                print(f"{fn.name}({args})")
                if(fn.name == "generate_ans_from_corpus"):
                    
#                     address = generate_address(message)
#                     if address == None:
#                         query = message
#                     else:
#                         query = f'''
# target location: {address}
# message: {message} 
#                         '''
#                     print(query)
                    corpus_agent_response = generate_ans_from_corpus(query=message, filters=filters)
                    return corpus_agent_response
            else:
                print(part.text)
                return part.text

        final_response = chat.send_message(f"\ncorpus agent response: {corpus_agent_response}")
        print("\nfinal response:")
        print(final_response)
        return final_response

if __name__=="__main__":
    generation_config = {
        "temperature": 0.5,
    }

    agent = ChatAgent(
        model_name="gemini-1.5-pro",
        config=generation_config,
        tools = [
            genai.protos.Tool(
                function_declarations = [
                    genai.protos.FunctionDeclaration(
                        name = "generate_ans_from_corpus",
                        description = "Retrieves an answer using the corpus agent, which performs Retrieval Augmented Generation (RAG) to answer based on recent or realtime information."
                    ),
                ],
            ),
        ],
        tool_config={'function_calling_config':'ANY'},
    )

    filters = {
        "min_lat":24.0,
        "max_lat":30.0,
        "min_lng":115.0,
        "max_lng":125.0,
        "current_time": "2024-10-19 00:00:00",
        "time_range": 60
    }

    agent.chat("Are there any dangerous events?", filters=filters)
>>>>>>> Kent
