import requests
from app.retriever import Retriever
from app.embedding import Embedder
from app.config import OPENROUTER_API_KEY

class Generator:
    def __init__(self):
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }

    def generate(self, prompt: str, conversation_history=None, temperature=0.6, max_tokens=256, style="detailed") -> str:
        if style == "brief":
            prompt += "\n\nRespond concisely in 1-2 short sentences, no more than 100 words."
        else:
            prompt += "\n\nRespond clearly and informatively, but keep answer under 500 characters."
        
        system_message = {
            "role": "system",
            "content": (
                "Role: You are an AI assistant helping users with information about Indium Technologies. "
                "Action: You should answer questions based on the context provided from the Indium knowledge base and previous conversation. "
                "Context: The context includes both the retrieved documents related to Indium Technologies and any prior conversation the user has had with you. "
                "Execute: Your response should be clear, concise, and informative. If the user’s question requires more detailed information, make sure to explain with examples or provide a link to more in-depth resources."
            )
        }

        messages = [system_message]
        if conversation_history:
            for msg in conversation_history[:-1][-10:]:
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })

        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": "mistralai/mistral-7b-instruct",
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        response = requests.post(self.api_url, headers=self.headers, json=payload)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()


class RAGChain:
    def __init__(self, retriever: Retriever, generator: Generator):
        self.retriever = retriever
        self.generator = generator
        self.embedder = Embedder()

    def answer_question(self, question: str, conversation_history=None) -> str:
        docs = self.retriever.retrieve(question)
        context = "\n\n".join([doc['content'] for doc in docs])

        # Defination of RACE-formatted prompt
        prompt = f"""
        Role: You are an AI assistant providing information about Indium Technologies. 
        Action: Answer the user's question based on the provided context, using the relevant documents to support your answer. 
        Context: Here’s some information from our knowledge base:\n\n{context}\n\nQuestion: {question}
        Execute: Provide a clear, accurate, and concise response. If needed, summarize the information or provide a link to more detailed resources.
        """

        response = self.generator.generate(prompt, conversation_history=conversation_history)
        return response
