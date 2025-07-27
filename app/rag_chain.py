import requests
from app.config import OPENROUTER_API_KEY
from app.retriever import Retriever

class Generator:
    def __init__(self):
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "HTTP-Referer": "http://localhost:8000", # Replace with your site URL
            "Content-Type": "application/json"}

    def generate(self, prompt: str) -> str:
        try:
            print("🧠 Prompt:", prompt)
            payload = {
                "model": "mistralai/mistral-7b-instruct",
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant that answers questions based on the given context."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 512}
            
            response = requests.post(self.api_url, headers=self.headers, json=payload)
            response.raise_for_status()
            json_response = response.json()
            if "choices" in json_response and len(json_response["choices"]) > 0:
                return json_response["choices"][0]["message"]["content"]
            else:
                return f"Unexpected API response format: {json_response}"
        except Exception as e:
            return "Sorry, I couldn't generate an answer at this time."

class RAGChain:
    def __init__(self, retriever: Retriever, generator: Generator):
        self.retriever = retriever
        self.generator = generator

    def answer_question(self, question: str):
        docs = self.retriever.retrieve(question)
        if not docs:
            return "I couldn’t find anything relevant to your question."
        context = "\n\n".join([doc['content'] for doc in docs])
        prompt = f"Context:\n{context}\n\nQuestion: {question}\nAnswer:"
        return self.generator.generate(prompt)