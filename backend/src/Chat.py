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
    # answer, answerable_prob = corpus_agent.generate_answer(filters=filters, query=query, answer_style="VERBOSE")
    # print("in gen ans from")
    # print(answer)
    response = corpus_agent.query_corpus(filters, query)
    print("\n\nresponse from corpus")
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
        # print(text)
    print("\n\ncontext:")
    print(context)
    print("\n\nreference")
    # for i, item in enumerate(reference, 1):
    #     item = json.dumps(item, indent=4)
    #     print(item)
    print(reference)
    return context, reference
        
def answer_on_your_own(answer:str):
    return answer

def parse_response(response):
    answer = ""
    print(response.parts)
    for part in response.parts:
        if fn := part.function_call:
            args = ", ".join(f"{key}={val}" for key, val in fn.args.items())
            print(f"{fn.name}({args})")
            if(fn.name == "query_corpus"):
                return "query_corpus"
            elif(fn.name == "answer_on_your_own"):
                for key, val in fn.args.items():
                    if key == "answer":
                        answer = val
                return answer
        else:
            print(part.text)
            answer += part.text
    print(answer)
    return answer


class ChatAgent():
    def __init__(self):
        # chat = None,
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
            system_instruction='''
            You are a model with two answer mode.
            1. answer on your own
            2. query Corpus
            Based on "question" in the user request, If recent or realtime information is needed call the corpus agent for crowd sourced information.
            otherwise, just call function "answer_on_your_own" and answer the question on your own, pass it as a args
            - mind the example of realtime info: traffic, wether, store 
            After context is given,  which is composed of crowd sourced information, answer based on the following steps:
            1. If the question involves degree of distance, such as 'nearby', 'close', 'within walking distance', evaluate the distance by estimating the distance between the two coordinates.
            2. anwswer based on the contexts
            IMPORTANT: do not call function after context is provided.!!!

            Otherwise answer freely.
            '''
        )
        return
    
    
    
    # def start_chat(self):
    #     if self.chat ==None:
    #         self.chat = self.model.start_chat()
    
    def chat(self, message, filters, current_lat, current_lng):
        chat = self.model.start_chat()
        query = f'''
        my location: ({current_lat},{current_lng})
        question: {message} 
        '''
        print("query: ")
        print(query)
        response = chat.send_message(query)

        answer = parse_response(response)
        if answer == "query_corpus":
            context, reference = generate_context(query=query, filters=filters)
            response2 = chat.send_message(context)
            print(response2)
            print(chat.history)
            answer2 = parse_response(response2)
            return answer2, reference

        

        print(answer)
        return answer, None

        

if __name__=="__main__":

    agent = ChatAgent()

    filters = {
        "min_lat":24.0,
        "max_lat":30.0,
        "min_lng":115.0,
        "max_lng":125.0,
        "current_time": "2024-10-19 00:00:00",
        "time_range": 60
    }
    # agent.start_chat()
    agent.chat(message="Are there dangerous acitivity nearby?", filters=filters, current_lat=25.09871, current_lng=121.9876)