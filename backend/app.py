
from services.embeddings import create_embeddings
from services.chunker import chunk_text
from services.pdf_processor import extract_text_from_pdf
from flask import Flask, request, jsonify
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

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

    return jsonify({
    "message": "PDF uploaded successfully",
    "filename": filename,
    "characters_extracted": len(extracted_text),
    "total_chunks": len(chunks),
    "embedding_shape": list(embeddings.shape)
})

if __name__ == "__main__":
    app.run(debug=True)