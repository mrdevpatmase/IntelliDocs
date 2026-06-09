import requests


def generate_answer(question, context):

    prompt = f"""
You are a document QA assistant.

STRICT RULES:

- Use ONLY information explicitly present in the context.
- NEVER infer.
- NEVER estimate.
- NEVER assume.
- NEVER use outside knowledge.
- If a value is not explicitly written in the context, say:
  "Information not found in the document."
- Answer in bullet points.
- Maximum 6 bullet points.

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