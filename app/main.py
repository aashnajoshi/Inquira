from app.rag_chain import RAGChain, Generator
from app.retriever import Retriever
from app.embedding import Embedder
from app.vector_store import VectorStore
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
docs_path = BASE_DIR / "data" / "documents.json"
static_dir = BASE_DIR / "app" / "static"
app = FastAPI()
app.mount("/static", StaticFiles(directory=static_dir), name="static")

with open(docs_path, encoding="utf-8") as f:
    docs = json.load(f)

embedder = Embedder()
vector_store = VectorStore(dimension=768)
texts = [doc['content'] for doc in docs]
embeddings = embedder.embed_texts(texts)
vector_store.add(embeddings, docs)
retriever = Retriever(embedder, vector_store)
generator = Generator()
rag_chain = RAGChain(retriever, generator, docs, vector_store)

@app.get("/", response_class=FileResponse)
async def serve_chat_ui():
    return FileResponse(static_dir / "chat.html")

@app.post("/ask")
async def ask(request: Request):
    data = await request.json()
    question = data.get("question")
    if not question:
        return {"answer": "Please provide a question."}
    answer = rag_chain.answer_question(question)
    return {"answer": answer}