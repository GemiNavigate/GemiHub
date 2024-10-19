import google.generativeai as genai
from google.oauth2 import service_account
from dotenv import load_dotenv
from Corpus import CorpusAgent
from typing import Dict
import json
from jsonschema import validate
import uuid
import os
from typing import Optional, List, Dict
from Corpus import CorpusAgent
import json

# set keys
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)
DEV_DOC=os.getenv("TEST_DOCUMENT")

def generate_context(query: str, filters: Dict[str, Dict]) -> Dict[str, float]:
    corpus_agent = CorpusAgent(document=DEV_DOC)
    response = corpus_agent.query_corpus(filters, query)
    context = ""
    reference = []
    i = 0
    for item in response:
        text = item.chunk.data.string_value
        metadata = item.chunk.custom_metadata
        lat = metadata[0].numeric_value
        lng = metadata[1].numeric_value
        timestamp = metadata[2].numeric_value
        
        context += f"context {i}:\nlocation: ({lat}, {lng})\ninformation: {text.lstrip()}\n"
        i += 1
        ref = {
            "info": text, 
            "lat": lat,
            "lng": lng,
            "time": timestamp,
        }
        reference.append(ref)
    return context, reference
        
def answer_on_your_own(answer:str):
    return answer

def parse_response(response):
    answer = ""
    for part in response.parts:
        if fn := part.function_call:
            args = ", ".join(f"{key}={val}" for key, val in fn.args.items())
            if(fn.name == "query_corpus"):
                return "query_corpus"
            elif(fn.name == "answer_on_your_own"):
                for key, val in fn.args.items():
                    if key == "answer":
                        answer = val
                return answer
        else:
            answer += part.text
    return answer

def load_system_instruction(file_path: str) -> str:
    try:
        with open(file_path, 'r') as f:
            return f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"System instruction file not found: {file_path}")


class ChatAgent():
    def __init__(self):
        # chat = None,
        instruction = load_system_instruction("system_instruction_ask_filter.txt")
        self.model = genai.GenerativeModel(
            model_name="gemini-1.5-pro",
            generation_config = {
                "temperature": 0.0,
                "top_p": 0.95,
                "top_k": 64,
                "max_output_tokens": 8192,
                "response_mime_type": "text/plain",
            },
            tools=[
                genai.protos.Tool(
                    function_declarations = [
                        genai.protos.FunctionDeclaration(
                        name = "query_corpus",
                        description = "Retrieves relevant recent or realtime information about the query",
                        ),
                        # genai.protos.FunctionDeclaration(
                        # name = "answer_on_your_own",
                        # description = "answer question on your own",
                        
                        # ),
                    ],
                ),
                answer_on_your_own
            ],
            tool_config={'function_calling_config':'ANY'},
            system_instruction=instruction,
        )
        return
    
    
    def chat(self, message, filters, current_lat, current_lng):
        chat = self.model.start_chat()
        query = f'''
        my location: ({current_lat},{current_lng})
        question: {message} 
        '''
        response = chat.send_message(query)

        answer = parse_response(response)
        if answer == "query_corpus":
            context, reference = generate_context(query=query, filters=filters)
            response2 = chat.send_message(context)
            answer2 = parse_response(response2)
            print('\n')
            
            final_answer = f"Based on crowd sourced answer:\n {answer2} "
            print(final_answer)
            return final_answer, reference

        

        return answer, None

        

if __name__=="__main__":

    agent = ChatAgent()

    filters = {
        "min_lat": -90,
        "max_lat": 90,
        "min_lng": -180,
        "max_lng": 180,
        "cur_time": "2024-10-19 12:09:57",
        "time_range": 10
    }
    # agent.start_chat()
    agent.chat(message="tell me how many people here", filters=filters, current_lat=-90, current_lng=180)


    '''
    {
      "content": "tell me how many people here",
      "cur_lat": -90,
      "cur_lng": -180,
      "filter": {
        "min_lat": -90,
        "max_lat": 90,
        "min_lng": -180,
        "max_lng": 180,
        "cur_time": "2024-10-19T12:09:57.034Z",
        "time_range": 10
      }
    }
    '''

    print(DEV_DOC)
    corpus_agent = CorpusAgent(document=DEV_DOC)
    
    content = '''location: (30.0988, 121.98765) Information: Whoa a traffic accident! Send Help! '''
    corpus_agent.add_info_to_document(content=content, lat=30.0988, lng=121.98765, time="2024-10-19 10:00:00")
