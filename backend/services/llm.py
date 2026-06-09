import requests


def generate_answer(question, context):

    prompt = f"""
You are a document QA assistant.

Rules:

- Use ONLY the provided context.
- Never infer.
- Never estimate.
- Never use outside knowledge.
- If information is missing, reply:
  Information not found in the document.
- Answer in bullet points.
- Maximum 4 bullet points.
- Each bullet must be under 20 words.
- Include exact values when available.

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