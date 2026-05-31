# services/retriever.py

import faiss
import numpy as np

index = None


def create_faiss_index(embeddings):
    global index

    dimension = embeddings.shape[1]

    index = faiss.IndexFlatL2(dimension)

    index.add(np.array(embeddings, dtype=np.float32))

    return index


def search_chunks(query_embedding, k=3):
    distances, indices = index.search(
        np.array([query_embedding], dtype=np.float32),
        k
    )

    return indices[0]