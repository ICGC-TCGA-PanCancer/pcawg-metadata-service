import os

DEBUG = True

ES_HOST = os.getenv("ES_HOST", "localhost")
ES_PORT = int(os.getenv("ES_PORT", "9200"))
ES_INDEX = "p_150507193855"

API_HOST = os.getenv("API_HOST", "localhost")
API_PORT = int(os.getenv("API_PORT", "5000"))
