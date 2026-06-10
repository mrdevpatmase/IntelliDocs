import requests

def generate_answer(question, context):

    prompt = f"""
    You are an expert document question-answering assistant.

    STRICT RULES:

    1. Use ONLY information present in the context.
    2. Never use outside knowledge.
    3. Never estimate.
    4. Never hallucinate.
    5. Never invent values.
    6. If the answer is not present in the context, reply exactly:
    Information not found in the document.

    ANSWER RULES:

    1. Answer in bullet points.
    2. Maximum 4 bullet points.
    3. Keep answers concise.
    4. Use exact values from the context.
    5. Do not explain your reasoning.
    6. Do not mention the context unless asked.

    TABLE RULES:

    1. The context may contain tables converted into plain text.
    2. When table headers and row values are present, map values according to their column order.
    3. If a value exists in a table row, return it.
    4. Do not say information is missing if the value is clearly present in a table.
    5. Use only explicitly available values.

    CONTEXT:
    {context}

    QUESTION:
    {question}

    ANSWER:
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
