import requests
from config import OPENROUTER_API_KEY
from retriever import Retriever
from urllib.parse import urlparse
import re

class Generator:
    def __init__(self):
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "HTTP-Referer": "http://localhost:8000",
            "Content-Type": "application/json"
        }

    def generate(self, prompt: str, temperature=0.6, max_tokens=256, style="detailed") -> str:
        if style == "brief":
            prompt += "\n\nRespond concisely in 1-2 short sentences, no more than 100 words."
        else:
            prompt += "\n\nRespond clearly and informatively, but keep answer under 500 characters."

        payload = {
            "model": "mistralai/mistral-7b-instruct",
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a helpful assistant answering questions about Indium Technologies. "
                        "Answer only based on the provided context. Keep tone conversational and concise. "
                        "Do not include source links in the response body."
                    )
                },
                {"role": "user", "content": prompt}
            ],
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        response = requests.post(self.api_url, headers=self.headers, json=payload)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()

def extract_title_from_url(url: str, docs: list[dict]) -> str:
    for doc in docs:
        if doc.get("metadata", {}).get("url") == url:
            return doc["metadata"].get("title", "Link")
    path = urlparse(url).path.strip("/")
    if not path:
        return "Homepage"
    title = path.split("/")[-1].replace("-", " ").replace("_", " ").title()
    return title or "Link"

class RAGChain:
    def __init__(self, retriever: Retriever, generator: Generator, docs: list[dict]):
        self.retriever = retriever
        self.generator = generator
        self.docs = docs

    def is_small_talk(self, question: str) -> bool:
        casual_keywords = r"\b(hi|hello|hey|bye|thanks|thank you|cool|awesome|okay|who are you|your name|welcome)\b"
        return bool(re.search(casual_keywords, question.lower()))

    def handle_small_talk(self, question: str) -> str:
        prompt = f"You are a friendly chatbot. Reply naturally to: {question}"
        return self.generator.generate(prompt, temperature=0.8, max_tokens=40, style="brief")

    def classify_query(self, question: str) -> str:
        return "brief" if len(question.strip().split()) <= 5 else "detailed"

    def answer_question(self, question: str) -> str:
        if self.is_small_talk(question):
            return self.handle_small_talk(question)

        docs = self.retriever.retrieve(question)
        context = "\n\n".join([doc['content'] for doc in docs if doc.get('content')])
        links = list({doc.get("metadata", {}).get("url", "") for doc in docs if doc.get("metadata", {}).get("url")})
        prompt = f"Here’s some info about Indium Technologies:\n\n{context}\n\nQuestion: {question}"
        style = self.classify_query(question)
        response = self.generator.generate(prompt, style=style)

        if links:
            link_texts = [f"[{extract_title_from_url(url, self.docs)}]({url})" for url in links]
            response += f"\n\nSource: {', '.join(link_texts)}"

        return response