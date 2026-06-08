from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")


def create_query_embedding(query):
    return model.encode(query)


def create_embeddings(chunks):

    if isinstance(
        chunks[0],
        dict
    ):
        texts = [
            chunk["text"]
            for chunk in chunks
        ]
    else:
        texts = chunks

    return model.encode(texts)