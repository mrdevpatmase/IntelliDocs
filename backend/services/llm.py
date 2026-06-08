import requests


def generate_answer(question, context):

    prompt = f"""
You are an AI research assistant.

Answer the question using ONLY the provided context.

If the answer exists in the context:
- Give a concise answer.
- Include important numbers if available.

If the answer does not exist:
Information not found in the document.

Context:
{context}

Question:
{question}

Answer:
"""

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "phi3",
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0,
                "num_predict": 100
            }
        }
    )

    return response.json()["response"].strip()