import google.genai as genai
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

def generate_answer(context: str, question: str) -> str | None:

    prompt = f"""
You are a helpful assistant that answers questions based on the provided context.
Answer the question using the context below. If the context doesn't contain enough information, say so but try your best.

Context:
{context}

Question:
{question}

Answer:
"""
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text