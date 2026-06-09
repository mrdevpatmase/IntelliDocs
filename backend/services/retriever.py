import faiss
import numpy as np
import pickle
import os

index = None
stored_chunks = []


def create_faiss_index(
    embeddings,
    chunks
):

    global index
    global stored_chunks

    embeddings = np.array(
        embeddings,
        dtype=np.float32
    )

    if index is None:

        print(">>> Creating NEW index")

        dimension = embeddings.shape[1]

        index = faiss.IndexFlatL2(
            dimension
        )

        index.add(
            embeddings
        )

        stored_chunks = chunks

    else:

        print(">>> Adding to EXISTING index")

        index.add(
            embeddings
        )

        stored_chunks.extend(
            chunks
        )

    print(">>> Total vectors:", index.ntotal)
    print(">>> Total chunks:", len(stored_chunks))


def search_chunks(
    query_embedding,
    k=4
):

    global index

    if index is None:
        raise Exception(
            "FAISS index not loaded."
        )

    distances, indices = index.search(
        np.array(
            [query_embedding],
            dtype=np.float32
        ),
        k
    )

    return indices[0]


def save_index():

    global index
    global stored_chunks

    os.makedirs(
        "vector_store",
        exist_ok=True
    )

    faiss.write_index(
        index,
        "vector_store/index.faiss"
    )

    with open(
        "vector_store/metadata.pkl",
        "wb"
    ) as f:

        pickle.dump(
            stored_chunks,
            f
        )


def load_index():

    global index
    global stored_chunks

    if not os.path.exists(
        "vector_store/index.faiss"
    ):
        return False

    index = faiss.read_index(
        "vector_store/index.faiss"
    )

    with open(
        "vector_store/metadata.pkl",
        "rb"
    ) as f:

        stored_chunks = pickle.load(
            f
        )

    return True


def get_relevant_chunks(
    indices
):

    global stored_chunks

    return [
        stored_chunks[i]
        for i in indices
    ]


def delete_document(document_name):

    global stored_chunks
    global index

    # Remove document chunks
    stored_chunks = [

        chunk

        for chunk in stored_chunks

        if chunk["document"] != document_name

    ]

    # No documents left
    if len(stored_chunks) == 0:

        index = None

        if os.path.exists(
            "vector_store/index.faiss"
        ):
            os.remove(
                "vector_store/index.faiss"
            )

        if os.path.exists(
            "vector_store/metadata.pkl"
        ):
            os.remove(
                "vector_store/metadata.pkl"
            )

        return

    # Recreate embeddings
    from services.embeddings import (
        create_embeddings
    )

    texts = [

        chunk["text"]

        for chunk in stored_chunks

    ]

    embeddings = create_embeddings(
        texts
    )

    # Rebuild index
    dimension = embeddings.shape[1]

    index = faiss.IndexFlatL2(
        dimension
    )

    index.add(
        np.array(
            embeddings,
            dtype=np.float32
        )
    )

    save_index()