from services.llm import generate_answer
from services.embeddings import create_query_embedding
from services.retriever import (
    save_index,
    load_index,
    search_chunks,
    get_relevant_chunks
)
from services.retriever import create_faiss_index
from services.embeddings import create_embeddings
from services.chunker import chunk_text
from services.pdf_processor import extract_text_from_pdf
from flask import Flask, request, jsonify
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

load_index()

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

    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)

    file.save(filepath)

    extracted_text = extract_text_from_pdf(filepath)
    chunks = chunk_text(extracted_text)
    embeddings = create_embeddings(chunks)
    create_faiss_index(embeddings, chunks)
    save_index()

    
    return jsonify({
    "message": "PDF uploaded successfully",
    "total_chunks": len(chunks),
    "embedding_shape": list(embeddings.shape),
    "faiss_vectors": embeddings.shape[0]
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

    context = "\n\n".join(chunks)

    answer = generate_answer(
    question,
    context
)

    return jsonify({
    "question": question,
    "answer": answer
})

if __name__ == "__main__":
    app.run(debug=True)