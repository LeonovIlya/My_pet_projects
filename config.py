import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")
WEATHER_API = os.getenv("WEATHER_API")
GS_ID = os.getenv("GS_ID")
FILENAME_GS = os.getenv("FILENAME_GS")
