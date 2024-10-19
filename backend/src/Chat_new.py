import google.generativeai as genai
from google.oauth2 import service_account
from dotenv import load_dotenv
import os
from typing import Optional, List, Dict
from Corpus import CorpusAgent
import json

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)
DEV_DOC=os.getenv("TEST_DOCUMENT")

class ChatAgent():
    def __init__(self):
        # self.session_ID = session_ID
        
        generation_config = {
            "temperature": 0.0,
        }
        self.model = genai.GenerativeModel(
            model_name="gemini-1.5-pro",
            generation_config=generation_config,
            tools = [
                genai.protos.Tool(
                    function_declarations = [
                        genai.protos.FunctionDeclaration(
                            name = "generate_context",
                            description = "Retrieves an answer using the corpus agent, which performs Retrieval Augmented Generation (RAG) to answer based on recent or realtime information."
                        ),
                    ],
                ),
            ],
            tool_config={'function_calling_config':'ANY'},
            system_instruction='''
                You are a chat agent that works together with a corpus agent, which performs RAG on a corpus consisting of crowd sourced information on recent or realtime events.
                Call the corpus agent when the user asks for events or current status of their surrounding or a specific location, otherwise answer directly.
                Make sure you have pending the user query word by word.
                If no need to ask corpus, then just answer on your own.
            '''
        )
        # You need to decide whether the user is asking about the information about a place first.
        #             - example about a question asking the infromation of a place: Is there any traffic accidents?
        #             - example about a question NOT asking the information of a place: Have you have dinner?
        #         If the user is asking about the information about a place, then call function "generate_ans_from_corpus".
        #         else, answer directly.
        
    def chat(self, request: Dict[str, Dict]):
        chat = self.model.start_chat()
        response = chat.send_message(request["query"])
        
        for part in response.parts:
            if fn := part.function_call:
                args = ", ".join(f"{key}={val}" for key, val in fn.args.items())
                # print(f"{fn.name}({args})")
                if(fn.name == "generate_context"):
                    metadata_filters = request["filter"]
                    query = request["query"]
                    corpus_agent_response = self.generate_context(query=query, filters=metadata_filters)
                    if corpus_agent_response["answerable_probability"] > 0:
                        final_response = chat.send_message(f"\ncorpus agent response: {corpus_agent_response}")
                    else:
                        final_response = corpus_agent_response["answer"]
                    # print("\nfinal response:")
                    # print(final_response)
                    return final_response
            else:
                print(part.txt)
                return part.txt

    def generate_context(self, query: str, filters: Dict[str, Dict]) -> Dict[str, float]:
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
            
            query += f"context {i}:\nlocation: ({lat}, {lng})\ninformation: {text.lstrip()}\n"
            i += 1
            ref = {
                "info": text, 
                "lat": lat,
                "lng": lng,
                "time": timestamp,
            }
            reference.append(ref)
            # print(text)
        print("\n\nquery:")
        print(context)
        print("\n\nreference")
        for i, item in enumerate(reference, 1):
            item = json.dumps(item, indent=4)
            print(item)
        print(reference)
        return context, reference
        
    
if __name__=="__main__":
    request = {
        "query": "Is there any traffic accident?",
        "filter": {
            "min_lat": 25.0,
            "max_lat": 26.0,
            "min_lng": 121.0,
            "max_lng": 122.0,
            "current_time": "2024-10-18 20:30:00",
            "time_range": 60,
        }
    }
    agent = ChatAgent()
    
    agent.chat(request)