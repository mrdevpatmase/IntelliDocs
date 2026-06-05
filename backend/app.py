from services.llm import generate_answer
from services.embeddings import (
    create_query_embedding,
    create_embeddings
)
import services.retriever as retriever
from services.retriever import (
    save_index,
    load_index,
    search_chunks,
    get_relevant_chunks,
    create_faiss_index
)
from services.chunker import chunk_text
from services.pdf_processor import extract_text_from_pdf

from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

loaded = load_index()
print("Index loaded:", loaded)

if loaded:
    print("Loaded vectors:", retriever.index.ntotal)
    print("Loaded chunks:", len(retriever.stored_chunks))

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


@app.route("/")
def home():
    return "IntelliDocs Backend Running"


@app.route("/upload", methods=["POST"])
def upload_pdf():

    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    if not file.filename.lower().endswith(".pdf"):
        return jsonify({"error": "Only PDF files are allowed"}), 400

    filename = secure_filename(file.filename)

    filepath = os.path.join(
        app.config["UPLOAD_FOLDER"],
        filename
    )

    file.save(filepath)

    # Page-aware extraction
    pages = extract_text_from_pdf(filepath)

    # Metadata-aware chunking
    chunks = chunk_text(pages)

    # Add document name to every chunk
    for chunk in chunks:
        chunk["document"] = filename

    embeddings = create_embeddings(chunks)

    create_faiss_index(
        embeddings,
        chunks
    )

    save_index()

    return jsonify({
        "message": "PDF uploaded successfully",
        "document": filename,
        "total_chunks": len(chunks),
        "embedding_shape": list(embeddings.shape),
        "faiss_vectors": retriever.index.ntotal
    })


@app.route("/ask", methods=["POST"])
def ask_question():

    data = request.get_json()

    question = data.get("question")

    if not question:
        return jsonify({
            "error": "Question is required"
        }), 400

    query_embedding = create_query_embedding(question)

    indices = search_chunks(query_embedding)

    chunks = get_relevant_chunks(indices)

    context = "\n\n".join(
        chunk["text"]
        for chunk in chunks
    )

    answer = generate_answer(
        question,
        context
    )

    sources = []

    seen = set()

    for chunk in chunks:

        source = (
            chunk["document"],
            chunk["page"]
        )

        if source not in seen:

            seen.add(source)

            sources.append({
                "document": chunk["document"],
                "page": chunk["page"]
            })

    return jsonify({
        "question": question,
        "answer": answer,
        "sources": sources
    })

import services.retriever as retriever

@app.route("/documents", methods=["GET"])
def list_documents():

    unique_docs = list({
        chunk["document"]
        for chunk in retriever.stored_chunks
    })

    return jsonify({
        "documents": unique_docs,
        "total_documents": len(unique_docs)
    })

if __name__ == "__main__":
    app.run(debug=True)