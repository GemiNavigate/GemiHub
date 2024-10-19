import google.generativeai as genai
from google.oauth2 import service_account
from dotenv import load_dotenv
import os
from typing import Optional, List, Dict
from Corpus import CorpusAgent
from google.ai.generativelanguage_v1beta.types import content

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
                            name = "generate_ans_from_corpus",
                            description = "Retrieves an answer using the corpus agent, which performs Retrieval Augmented Generation (RAG) to answer based on recent or realtime information."
                        ),
                    ],
                ),
            ],
            tool_config={'function_calling_config':'ANY'},
        )
        
    def chat(self, request: Dict[str, Dict]):
        chat = self.model.start_chat()
        metadata_filters = request["filter"]
        query = request["query"]
        corpus_agent_response = self.generate_ans_from_corpus(query=query, filters=metadata_filters)
        final_response = chat.send_message(f"\ncorpus agent response: {corpus_agent_response}")
        print("\nfinal response:")
        print(final_response)
        return final_response

    def generate_ans_from_corpus(self, query: str, filters: Dict[str, Dict]) -> Dict[str, float]:
        corpus_agent = CorpusAgent(document=DEV_DOC)
        answer, answerable_prob = corpus_agent.generate_answer(filters=filters, query=query, answer_style="VERBOSE")
        
        return {
            "answer": answer,
            "answerable_probability": answerable_prob
        }

if __name__=="__main__":
    request = {
        "query": "Is there any traffic accidents?",
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