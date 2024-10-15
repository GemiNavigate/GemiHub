import google.ai.generativelanguage as glm
from google.oauth2 import service_account
from dotenv import load_dotenv
import os


class CorpusAgent:
    def __init__(self, corpus_name, model_name):
        self.corpus_name = corpus_name
        self.model_name = model_name
        return

    def create_document(self, content):
        return

    def query_corpus(self):
        return
    
    def generate_answer(self, rag_service, prompt):
        return
    

    

if __name__ == "__main__":
    pass