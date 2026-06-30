import os
import numpy as np
import requests

JINA_API_KEY = os.getenv("JINA_API_KEY")

JINA_URL = "https://api.jina.ai/v1/embeddings"

HEADERS = {
    "Authorization": f"Bearer {JINA_API_KEY}",
    "Content-Type": "application/json"
}


def _embed(texts):
    response = requests.post(
        JINA_URL,
        headers=HEADERS,
        json={
            "model": "jina-embeddings-v3",
            "input": texts
        },
        timeout=60
    )

    response.raise_for_status()

    data = response.json()["data"]

    return np.array(
        [item["embedding"] for item in data],
        dtype=np.float32
    )


def create_query_embedding(query):
    return _embed([query])[0]


def create_embeddings(chunks):

    if not chunks:
        return np.array([], dtype=np.float32)

    if isinstance(chunks[0], dict):
        texts = [chunk["text"] for chunk in chunks]
    else:
        texts = chunks

    return _embed(texts)