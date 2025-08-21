from fastapi import FastAPI, Request, Depends
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from langchain.chains import RetrievalQA
from app.retriever import Retriever
from app.vector_store import VectorStore
from app.rag_chain import RAGChain, Generator
from app.embedding import Embedder
import uuid
import json
from pathlib import Path
from typing import Dict, List, Optional

BASE_DIR = Path(__file__).resolve().parent.parent
docs_path = BASE_DIR / "data" / "documents.json"
static_dir = BASE_DIR / "app" / "static"
app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"],)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

class SessionManager:
    def __init__(self):
        self.sessions: Dict[str, List[Dict[str, str]]] = {}

    def get_session(self, session_id: str) -> List[Dict[str, str]]:
        if session_id not in self.sessions:
            self.sessions[session_id] = []
        return self.sessions[session_id]

    def add_message(self, session_id: str, role: str, content: str) -> None:
        session = self.get_session(session_id)
        session.append({"role": role, "content": content})

    def get_conversation_history(self, session_id: str) -> List[Dict[str, str]]:
        return self.get_session(session_id)

session_manager = SessionManager()
with open(docs_path, encoding="utf-8") as f:
    docs = json.load(f)

embedder = Embedder()
vector_store = VectorStore(dimension=768)
texts = [doc['content'] for doc in docs]
embeddings = embedder.embed_texts(texts)
vector_store.add(embeddings, docs)
retriever = Retriever(embedder, vector_store)
generator = Generator()
rag_chain = RAGChain(retriever, generator)

@app.get("/", response_class=FileResponse)
async def serve_chat_ui():
    return FileResponse(static_dir / "chat.html")

@app.post("/get_session_history")
async def get_session_history(request: Request):
    data = await request.json()
    session_id = data.get("session_id")
    if not session_id or session_id not in session_manager.sessions:
        return {"history": []}
    return {"history": session_manager.get_conversation_history(session_id)}

async def get_session_id(request: Request) -> str:
    data = await request.json()
    session_id = data.get("session_id")
    if not session_id:
        session_id = str(uuid.uuid4())
    return session_id

@app.post("/ask")
async def ask(request: Request, session_id: str = Depends(get_session_id)):
    data = await request.json()
    question = data.get("question")
    if not question: return {"answer": "Please provide a question.", "session_id": session_id}
    
    session_manager.add_message(session_id, "user", question)
    conversation_history = session_manager.get_conversation_history(session_id)
    answer, sources = rag_chain.answer_question(question, conversation_history)
    session_manager.add_message(session_id, "bot", answer)
    return {"answer": answer, "sources": sources, "session_id": session_id}
