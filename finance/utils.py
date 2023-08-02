from dotenv import load_dotenv
import os


def alpaca_keys():
    load_dotenv()
    alpaca_key = os.getenv("alpaca_api_key")
    alpaca_secret = os.getenv("alpaca_api_secret")
    return alpaca_key, alpaca_secret
