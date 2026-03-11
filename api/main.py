import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI
from pydantic import BaseModel
from rag.retriever import get_retriever
from rag.generator import generate_answer

app = FastAPI()

class QuestionRequest(BaseModel):
    question: str

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/ask")
async def ask(request: QuestionRequest):
    try:
        retriever = get_retriever()
        docs = retriever.invoke(request.question)
        context = "\n".join([d.page_content for d in docs])
        answer = generate_answer(context, request.question)
        return {"answer": answer}
    except Exception as e:
        return {"error": str(e)}