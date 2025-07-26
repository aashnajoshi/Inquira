from rag_chain import RAGChain, Generator
from retriever import Retriever
from embedding import Embedder
from vector_store import VectorStore
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import json
import os

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=FileResponse)
async def serve_chat_ui():
    return FileResponse("static/chat.html")

embedder = Embedder()
vector_store = VectorStore(dimension=384)
docs_path = os.path.join("..", "data", "documents.json")
with open(docs_path, encoding="utf-8") as f:
    docs = json.load(f)

texts = [doc['content'] for doc in docs]
embeddings = embedder.embed_texts(texts)
vector_store.add(embeddings, docs)
retriever = Retriever(embedder, vector_store)
generator = Generator()
rag_chain = RAGChain(retriever, generator)

@app.post("/ask")
async def ask(request: Request):
    data = await request.json()
    question = data.get("question")
    if not question:
        return {"answer": "Please provide a question."}
    answer = rag_chain.answer_question(question)
    return {"answer": answer}