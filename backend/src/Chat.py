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
from typing import Optional, List, Dict
from Corpus import CorpusAgent
from google.ai.generativelanguage_v1beta.types import content

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

DEV_DOC=os.getenv("TEST_DOCUMENT")

def generate_ans_from_corpus(query: str, filters: Dict[str, Dict]) -> Dict[str, float]:

    corpus_agent = CorpusAgent(document=DEV_DOC)
    answer, answerable_prob = corpus_agent.generate_answer(filters=filters, query=query, answer_style="VERBOSE")
    
    return {
        "answer": answer,
        "answerable_probability": answerable_prob
    }


def generate_address(query: str):
    generation_config = {
        "temperature": 0,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
    }
    model = genai.GenerativeModel(
        model_name="gemini-1.5-pro",
        generation_config=generation_config,
        system_instruction='''answer google map compatible alias of the targeted area in the query, if no areas are targeted respond with "No target Area" ''',
    )

    chat = model.start_chat()
    response = chat.send_message(query)
    address = None
    print("generate address: ")
    for part in response.parts:
        print(part.text)
        if (part.text != "No target Area \n"):
            address = part.text

    return address

class ChatAgent():
    def __init__(self, model_name, tools, tool_config, config, session_ID=None):
        self.session_ID = session_ID
        self.model = genai.GenerativeModel(
            model_name=model_name,
            generation_config=config,
            tools=tools,
            tool_config=tool_config,
            system_instruction='''
                You are a chat agent that works together with a corpus agent, which performs RAG on a corpus consisting of crowd sourced information on recent or realtime events.
                Call the corpus agent when the user asks for events or current status of their surrounding or a specific location, otherwise answer directly.
'''
        )
        return
    
    def chat(self, message):
        chat = self.model.start_chat()
        response = chat.send_message(message)

        for part in response.parts:
            if fn := part.function_call:
                args = ", ".join(f"{key}={val}" for key, val in fn.args.items())
                print(f"{fn.name}({args})")
                if(fn.name == "generate_ans_from_corpus"):
                    metadata_filters = generate_filter()
                    address = generate_address(message)
                    if address == None:
                        query = message
                    else:
                        query = f'''
target location: {address}
message: {message} 
                        '''
                    print(query)
                    corpus_agent_response = generate_ans_from_corpus(query=query, filters=metadata_filters)
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
        "temperature": 0.0,
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

    # filters = {
    #     "location": {
    #         "lat":12.36,
    #         "lng":112.65,
    #         "dst":5.0
    #     },
    #     "timestamp": {
    #         "current_time": "2024-10-16 09:47:00",
    #         "range": 60
    #     }
    # }

    agent.chat("Are there any traffic accidents in Taipei?")