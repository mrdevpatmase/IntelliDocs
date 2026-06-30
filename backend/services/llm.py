import os

from groq import Groq

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

MODEL = "llama-3.3-70b-versatile"


def generate_answer(question, context):

    prompt = f"""
You are a document QA assistant.

Rules:
- Use ONLY the provided context.
- Never use outside knowledge.
- Never infer missing values.
- If information is missing reply:
Information not found in the document.

Context:
{context}

Question:
{question}
"""

    response = client.chat.completions.create(
        model=MODEL,
        temperature=0,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content.strip()