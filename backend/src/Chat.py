import google.generativeai as genai
from google.oauth2 import service_account
from dotenv import load_dotenv
import os
from typing import Optional, List, Dict
import requests


load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

def Hello():
    '''
    Says Hello in the right way
    
    Args:
    
    Returns:
        desired response from greetings
    '''
    print("hello from function")
    return


class ChatAgent():
    def __init__(self, model_name, tools, config, session_ID=None):
        self.session_ID = session_ID
        self.model = genai.GenerativeModel(
            model_name=model_name,
            generation_config=config,
            tools=tools,
        )
        return
    
    def chat(self, message):
        chat = self.model.start_chat()
        response = chat.send_message(message)
        print(response)
        return
    
    

if __name__=="__main__":
    generation_config = {
        "temperature": 0.0,
    }

    agent = ChatAgent(
        model_name="gemini-1.5-pro",
        config=generation_config,
        tools=[Hello]
    )

    agent.chat("Hi")