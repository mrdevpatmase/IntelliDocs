from sentence_transformers import SentenceTransformer

print("Loading SentenceTransformer...")
model = SentenceTransformer("all-MiniLM-L6-v2")
print("Model loaded successfully.")


def create_query_embedding(query):
    print("Creating query embedding...")
    return model.encode(query)


def create_embeddings(chunks):
    print("create_embeddings() called")

    if not chunks:
        print("No chunks found")
        return []

    if isinstance(chunks[0], dict):
        texts = [chunk["text"] for chunk in chunks]
    else:
        texts = chunks

    print(f"Encoding {len(texts)} chunks...")
    embeddings = model.encode(texts)
    print("Embeddings created.")

    return embeddings