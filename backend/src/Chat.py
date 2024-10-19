import google.generativeai as genai
import google.ai.generativelanguage as glm
from google.oauth2 import service_account
from dotenv import load_dotenv
from Corpus import CorpusAgent
from typing import Dict
import json
from jsonschema import validate
import uuid
from datetime import datetime
import os
from typing import Optional, List, Dict
from Corpus import CorpusAgent
from google.ai.generativelanguage_v1beta.types import content

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

DEV_DOC=os.getenv("TEST_DOCUMENT")

def generate_context_Ann(self, query: str, filters: Dict[str, Dict]) -> Dict[str, float]:
    corpus_agent = CorpusAgent(document=DEV_DOC)
    # answer, answerable_prob = corpus_agent.generate_answer(filters=filters, query=query, answer_style="VERBOSE")
    # print("in gen ans from")
    # print(answer)
    response = corpus_agent.query_corpus(filters, query)
    print("\n\nresponse from corpus")
    query = ""
    i = 0
    for item in response:
        text = item.chunk.data.string_value
        metadata = item.chunk.custom_metadata
        lat = metadata[0].numeric_value
        lng = metadata[1].numeric_value
        # timestamp = metadata[2].numeric_value
        query += f"context {i}:\nlocation: ({lat}, {lng})\ninformation: {text.lstrip()}\n"
        i += 1
        # print(text)
    print("\n\nquery:")
    print(query)
    return query

def generate_context(query: str, filters):
    context, references = None, None
    return context, references

def parse_response(response, filters, current_lat, current_lng):
    answer = ""
    for part in response.parts:
        if fn := part.function_call:
            args = ", ".join(f"{key}={val}" for key, val in fn.args.items())
            print(f"{fn.name}({args})")
            if(fn.name == "query_corpus"):
                return "query_corpus"
        else:
            print(part.text)
            answer += part.text
    print(answer)
    return answer


class ChatAgent():
    def __init__(self):
        self.model = genai.GenerativeModel(
            chat = None,
            model_name="gemini-1.5-pro",
            generation_config = {
                "temperature": 1,
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
                    ],
                ),
            ],
            tool_config={'function_calling_config':'ANY'},
            system_instruction='''
If recent or realtime information is needed call the corpus agent for crowd sourced information
After context is given,  which is composed of crowd sourced information, answer based on the following steps:
1. If the question involves degree of distance, such as 'nearby', 'close', 'within walking distance', evaluate the distance by estimating the distance between the two coordinates.
2. anwswer based on the contexts
Let's think step by step.
Otherwise answer freely.
'''
        )
        return
    
    def start_chat(self):
        if self.chat ==None:
            self.chat = self.model.start_chat()
    
    def chat(self, message, filters, current_lat, current_lng):
        
        response = self.chat.send_message(message)

        answer = parse_response(response, filters, current_lat, current_lng)
        if answer == "query_corpus":
            query = f'''
my location: ({current_lat},{current_lng})
question: {message} 
'''
            context, reference = generate_context(query=query)
            response2 = self.chat.send_message(context)
            answer2 = parse_response(response2, filters, current_lat, current_lng)
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
    agent.start_chat()
    agent.chat(message="Are there any dangerous events?", filters=filters, current_lat=25.09871, current_lng=121.9876)