import requests


def generate_answer(question, context):

    prompt = f"""
Answer ONLY using the provided context.

Context:
{context}

Question:
{question}

If the answer is not present in the context,
reply:
Information not found in the document.
"""

    response = requests.post(
    "http://localhost:11434/api/generate",
    json={
        "model": "phi3",
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0
        }
    }
)

    return response.json()["response"]