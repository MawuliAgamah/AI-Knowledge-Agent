"""This file contains the configuration settings for models and codebase"""
import os
from dotenv import load_dotenv


# from pathlib import Path
# import logging
# from log import logger
# import sys

load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")


config = {
    "model": "gpt-3.5-turbo",
    "api_key": API_KEY
}
