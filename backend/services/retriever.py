# services/retriever.py

import faiss
import numpy as np

index = None
stored_chunks = []

def create_faiss_index(embeddings, chunks):
    global index
    global stored_chunks

    stored_chunks = chunks

    dimension = embeddings.shape[1]

    index = faiss.IndexFlatL2(dimension)

    index.add(np.array(embeddings, dtype=np.float32))


def search_chunks(query_embedding, k=3):
    distances, indices = index.search(
        np.array([query_embedding], dtype=np.float32),
        k
    )

    return indices[0]

def get_relevant_chunks(indices):
    global stored_chunks

    return [stored_chunks[i] for i in indices]