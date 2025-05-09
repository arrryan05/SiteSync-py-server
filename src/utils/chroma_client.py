# app/code_analyzer/chroma_client.py
import os
from chromadb import Client
from chromadb.config import Settings
from chromadb.utils.embedding_functions import CohereEmbeddingFunction

# 1) configure your Cohere key & model in .env
COHERE_KEY   = os.getenv("COHERE_API_KEY", "")
COHERE_MODEL = os.getenv("COHERE_MODEL_NAME", "embed-english-v2.0")

# 2) point at your running Chroma server
CHROMA_URL = os.getenv("CHROMA_SERVER_URL", "http://localhost:8000")

# 3) initialize client & embedding fn
client = Client(Settings(
    chroma_server_host=CHROMA_URL,
))
emb_fn = CohereEmbeddingFunction(
    api_key=COHERE_KEY,
    model_name=COHERE_MODEL,
)

def get_collection(name: str):
    return client.get_or_create_collection(
        name=name,
        # embedding_function=emb_fn
    )
