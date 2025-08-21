import requests
from app.retriever import Retriever
from app.embedding import Embedder
from app.config import OPENROUTER_API_KEY
import re

class Generator:
    def __init__(self):
        self.api_url="https://openrouter.ai/api/v1/chat/completions"
        self.headers={"Authorization":f"Bearer {OPENROUTER_API_KEY}","Content-Type":"application/json"}
    
    def generate(self,question: str,context: str,conversation_history=None,temperature=0.6,max_tokens=256,style="detailed") -> str:
        if style=="brief":
            constraint="\n\nRespond concisely in 1-2 short sentences, no more than 100 words."
        else:
            constraint="\n\nRespond clearly and informatively, but keep answer under 500 characters."
        system_message={"role":"system","content":"Role: You are an AI assistant helping users with information about Indium Technologies. Action: Answer questions based solely on the provided context from the Indium knowledge base and conversation history. Context: Includes retrieved documents and prior conversation. Execute: Provide clear, concise, informative responses. Do not include any URLs, links, or source references in the response text, as sources are handled separately. Avoid HTML or markup in responses."}
        prompt=f"""Here’s some information from our knowledge base:\n\n{context}\n\nQuestion: {question}{constraint}"""
        messages=[system_message]
        if conversation_history:
            for msg in conversation_history[:-1][-10:]:
                messages.append({"role":msg["role"],"content":msg["content"]})
        
        messages.append({"role":"user","content":prompt})
        payload={"model":"mistralai/mistral-7b-instruct","messages":messages,"temperature":temperature,"max_tokens":max_tokens}
        response=requests.post(self.api_url,headers=self.headers,json=payload)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()

class RAGChain:
    def __init__(self,retriever: Retriever,generator: Generator):
        self.retriever=retriever
        self.generator=generator
        self.embedder=Embedder()
    
    def answer_question(self,question: str,conversation_history=None) -> str:
        docs=self.retriever.retrieve(question)
        context="\n\n".join([doc['content'] for doc in docs])
        unique_sources={}
        for doc in docs:
            url=doc['metadata']['url']
            if url not in unique_sources:
                unique_sources[url]={"title":doc['metadata']['title'],"url":url}
        sources=list(unique_sources.values())
        response=self.generator.generate(question,context,conversation_history=conversation_history)
        response=re.sub(r'https?://[^\s"]+','',response)
        response=re.sub(r'<[^>]+>','',response)
        response=re.sub(r'"\s*(target|rel|class)="[^"]*"','',response)
        response=response.strip()
        return response,sources
