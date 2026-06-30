from dotenv import load_dotenv

load_dotenv()

from flask_jwt_extended import get_jwt_identity
from flask import send_from_directory, make_response
from flask_cors import CORS
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
    create_faiss_index
)
from services.chunker import chunk_text
from services.pdf_processor import extract_text_from_pdf

from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import json
import os



from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required,
)
from services.models import User
from dotenv import load_dotenv
from services.database import db

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_FOLDER = os.path.join(
    os.path.dirname(BASE_DIR),
    "frontend"
)



app = Flask(__name__)
CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
    "DATABASE_URL"
)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

app.config["JWT_SECRET_KEY"] = os.getenv(
    "JWT_SECRET_KEY",
    "super-secret-key-change-in-production"
)

jwt = JWTManager(app)


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
    return send_from_directory(
        FRONTEND_FOLDER,
        "index.html"
    )

@app.route("/<path:filename>")
def frontend_files(filename):
    return send_from_directory(
        FRONTEND_FOLDER,
        filename
    )

@app.route("/upload", methods=["POST"])
@jwt_required()
def upload_pdf():
    try:
        print("STEP 1: Upload request received")

        if "file" not in request.files:
            return jsonify({"error": "No file provided"}), 400

        file = request.files["file"]

        if file.filename == "":
            return jsonify({"error": "No file selected"}), 400

        if not file.filename.lower().endswith(".pdf"):
            return jsonify({"error": "Only PDF files are allowed"}), 400

        username = get_jwt_identity()

        original_filename = secure_filename(file.filename)
        filename = f"{username}_{original_filename}"

        filepath = os.path.join(
            app.config["UPLOAD_FOLDER"],
            filename
        )

        file.save(filepath)
        print("STEP 2: File saved")

        pages = extract_text_from_pdf(filepath)
        print(f"STEP 3: PDF extracted ({len(pages)} pages)")

        chunks = chunk_text(pages)
        print(f"STEP 4: Created {len(chunks)} chunks")

        for chunk in chunks:
            chunk["document"] = filename
            chunk["owner"] = username

        print("STEP 5: Starting embedding generation...")
        embeddings = create_embeddings(chunks)
        print("STEP 6: Embeddings created")

        create_faiss_index(embeddings, chunks)
        print("STEP 7: FAISS index created")

        save_index()
        print("STEP 8: Index saved")

        return jsonify({
            "message": "PDF uploaded successfully",
            "document": filename,
            "total_chunks": len(chunks),
            "embedding_shape": list(embeddings.shape),
            "faiss_vectors": retriever.index.ntotal
        })

    except Exception as e:
        import traceback
        print("=" * 60)
        print("UPLOAD ERROR")
        traceback.print_exc()
        print("=" * 60)

        return jsonify({
            "error": str(e)
        }), 500


@app.route("/ask", methods=["POST"])
@jwt_required()
def ask_question():

    data = request.get_json()

    question = data.get("question")
    selected_document = data.get("document")
    username = get_jwt_identity()

    print("Selected Document:", selected_document)

    if not question:
        return jsonify({
            "error": "Question is required"
        }), 400

    query_embedding = create_query_embedding(
        question
    )

    distances, indices = search_chunks(
        query_embedding
    )

    print("\n===== SEARCH RESULTS =====")

    chunks = []

    for d, idx in zip(distances, indices):

        chunk = retriever.stored_chunks[idx]

        # User isolation
        if chunk.get("owner") != username:
            continue

        # PDF filter
        if (
            selected_document and
            chunk["document"] != selected_document
        ):
            continue

        print(
            f"Distance: {d:.4f}"
        )

        print(
            f"Document: {chunk['document']}"
        )

        print(
            f"Page: {chunk['page']}"
        )

        print(
            chunk['text'][:200]
        )

        print("-" * 50)

        if d < 1.15:
            chunks.append(chunk)

    chunks = chunks[:3]

    context = ""

    for chunk in chunks:

        context += f"""
Document: {chunk['document']}
Page: {chunk['page']}

{chunk['text']}
"""

    print("\nQUESTION:")
    print(question)

    print("\nRETRIEVED CHUNKS:")

    for i, chunk in enumerate(chunks):

        print(f"\n--- CHUNK {i+1} ---")
        print("Document:", chunk["document"])
        print("Page:", chunk["page"])
        print(chunk["text"][:500])

    print("\n===== CONTEXT =====")
    print(context)
    print("===================")

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

    sources = sources[:3]

    return jsonify({
        "question": question,
        "answer": answer,
        "sources": sources
    })

import services.retriever as retriever

@app.route("/documents", methods=["GET"])
@jwt_required()
def list_documents():

    username = get_jwt_identity()

    unique_docs = list({
        chunk["document"]
        for chunk in retriever.stored_chunks
        if chunk.get("owner") == username
    })

    return jsonify({
        "documents": unique_docs,
        "total_documents": len(unique_docs)
    })

@app.route("/delete-document", methods=["POST"])
@jwt_required()
def delete_document():

    data = request.get_json()

    document_name = data.get("document")

    if not document_name:
        return jsonify({
            "error": "Document name required"
        }), 400

    # Delete from FAISS + metadata
    retriever.delete_document(
        document_name
    )

    # Delete actual PDF file
    filepath = os.path.join(
        app.config["UPLOAD_FOLDER"],
        document_name
    )

    if os.path.exists(filepath):
        os.remove(filepath)

    return jsonify({
        "message": f"{document_name} deleted successfully"
    })


@app.route("/pdf/<filename>")
def serve_pdf(filename):

    response = make_response(
        send_from_directory(
            app.config["UPLOAD_FOLDER"],
            filename
        )
    )

    response.headers.pop(
        "X-Frame-Options",
        None
    )

    response.headers["Access-Control-Allow-Origin"] = "*"

    return response


@app.route("/register", methods=["POST"])
def register():

    data = request.get_json()

    username = data.get("username")
    password = data.get("password")

    if not username or not password:

        return jsonify({
            "error": "Username and password required"
        }), 400

    existing_user = User.query.filter_by(
        username=username
    ).first()

    if existing_user:

        return jsonify({
            "error": "User already exists"
        }), 400

    new_user = User(
        username=username,
        password=generate_password_hash(password)
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify({
        "message": "User registered successfully"
    }), 201



@app.route("/login", methods=["POST"])
def login():

    data = request.get_json()

    username = data.get("username")
    password = data.get("password")

    user = User.query.filter_by(
        username=username
    ).first()

    if not user:

        return jsonify({
            "error": "Invalid username or password"
        }), 401

    if not check_password_hash(
        user.password,
        password
    ):

        return jsonify({
            "error": "Invalid username or password"
        }), 401

    token = create_access_token(
        identity=username
    )

    return jsonify({
        "token": token,
        "username": username
    }), 200

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(
        host="0.0.0.0",
        port=port
    )

    # 