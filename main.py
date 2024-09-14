import requests
from dotenv import load_dotenv
import os

load_dotenv("secrets.env")

ALERTZY_PASSWORD = os.getenv("ALERTZY_PASSWORD")
ALERTZY_ACCOUNT_KEY = os.getenv("ALERTZY_ACCOUNT_KEY")
ALERTZY_URL = "https://alertzy.app/send"

