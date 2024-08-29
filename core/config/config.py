import os 
from pathlib import Path
from dotenv import load_dotenv
import logging
import sys

from core.log import logger

load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")


config = {
    "model" :"gpt-3.5-turbo",
    "api_key" : API_KEY
}
    