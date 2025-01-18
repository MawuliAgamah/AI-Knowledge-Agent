"""This file contains the configuration settings for models and codebase"""
import os
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama

# from pathlib import Path
# import logging
# from log import logger
# import sys

load_dotenv()



config = {
    "model": "gpt-3.5-turbo",
    "api_key": os.getenv("OPENAI_API_KEY")
}



class OpenAIConfig:
    model = "gpt-3.5-turbo"
    key = os.getenv("OPENAI_API_KEY")

    
class OllamaConfig:
    def __init__(self, model_name="llama3.2:latest", llm=None):
        self.model_name = model_name
        self.llm = ChatOllama(model=self.model_name)

    def get_llm(self):
        return self.llm
