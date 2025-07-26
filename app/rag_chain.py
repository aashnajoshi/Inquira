import requests
import os
from retriever import Retriever
from config import HF_API_TOKEN

class Generator:
    def __init__(self):
        self.api_url = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.1"
        self.headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}

    def generate(self, prompt: str) -> str:
        try:
            print("🧠 Prompt:", prompt)
            response = requests.post(self.api_url, headers=self.headers, json={"inputs": prompt})
            response.raise_for_status()

            json_response = response.json()
            print("✅ HF response:", json_response)

            if isinstance(json_response, list) and "generated_text" in json_response[0]:
                return json_response[0]["generated_text"]
            elif isinstance(json_response, dict) and "generated_text" in json_response:
                return json_response["generated_text"]
            else:
                return f"⚠️ Unexpected HF response format: {json_response}"
        except Exception as e:
            print("❌ Error calling Hugging Face API:", str(e))
            print("🔁 Full response content:", getattr(response, 'text', 'No response'))
            return "Sorry, I couldn't generate an answer at this time."

class RAGChain:
    def __init__(self, retriever: Retriever, generator: Generator):
        self.retriever = retriever
        self.generator = generator

    def answer_question(self, question: str):
        docs = self.retriever.retrieve(question)
        print(f"🔍 Retrieved {len(docs)} documents for question: {question}")

        if not docs:
            return "I couldn’t find anything relevant to your question."

        context = "\n\n".join([doc['content'] for doc in docs])
        prompt = f"Context:\n{context}\n\nQuestion: {question}\nAnswer:"
        return self.generator.generate(prompt)