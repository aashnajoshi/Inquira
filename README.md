# RAG-Chatbot
RAG-Chatbot is an AI-powered assistant that uses Retrieval Augmented Generation (RAG) to answer questions about Indium’s services. It leverages semantic search and generative models to return intelligent, context-aware responses from a curated knowledge base.

## Features
- Retrieval-Augmented Generation (RAG) architecture.
- Semantic document search using Sentence Transformers.
- Vector similarity matching with FAISS.
- Language generation using Hugging Face Transformers (e.g., Mistral-7B).
- FastAPI-powered REST API for backend processing.
- Chat-ready frontend with real-time interaction.

## Usage
### All required libraries can be installed using a single-line command:
```bash
pip install -r requirements.txt
```

### While to run the code:
#### Local FastAPI server:
```bash
uvicorn app.main:app --reload
```

#### On browser:
Visit [http://localhost:8000](http://localhost:8000)

## Description about various files:
- **.env**: Contains Hugging Face API key used for generation.
- **app/main.py**: Entry point of the FastAPI app; handles routing and endpoints.
- **app/embedding.py**: Embeds input text into vector form using `all-MiniLM-L6-v2`.
- **app/vector_store.py**: Initializes and manages the FAISS vector index.
- **app/retriever.py**: Handles document retrieval using semantic similarity.
- **app/rag_chain.py**: Combines the retriever and generator into a complete RAG chain.
- **data/documents.json**: Contains the documents about Indium’s services that are used to answer user queries.
- **requirements.txt**: Lists all top-level Python dependencies.
- **vercel.json**: Deployment configuration file for Vercel hosting.
- **static/chat.html**: HTML file for the frontend chat interface.
- **static/chatbot.js**: JavaScript file handling frontend logic.
