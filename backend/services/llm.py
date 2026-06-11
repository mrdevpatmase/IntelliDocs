import requests

def generate_answer(question, context):

    prompt = f"""
    You are a document QA assistant.

    Rules:
    - Use ONLY the provided context.
    - Never use outside knowledge.
    - Never infer missing values.
    - Answer ONLY the user's question.
    - Return ONLY the final answer.
    - Do not explain your reasoning.
    - Do not create sections.
    - Do not write labels like:
    TABLE RESPONSE
    ANALYSIS
    EXPLANATION
    - Maximum 3 bullet points.
    - If information is missing, reply exactly:
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
                "num_predict": 100,
                "top_p": 0.1
            }
        }
    )

    return response.json()["response"].strip()
