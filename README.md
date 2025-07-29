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
### Basic setup and dependency management:
1. Install `pipenv` if you don't have it:
   ```bash
   pip install pipenv
   ```

2. Activate the virtual environment:
   ```bash
   pipenv shell
   ```

3. Install required libraries from the `Pipfile`:
   ```bash
   pipenv install
   ```
        or
    ```bash
    pip install -r requirements.txt
    ```

4. Ensure that the `.env` file contains your OpenRouter API key.

### While to run the code:
```bash
cd app
```
#### Local FastAPI server (uses static html based UI):
```bash
uvicorn main:app --reload
```
#### With Streamlit-UI (in separate terminal):
```bash
streamlit run st.py
```

#### On browser:
Visit [http://localhost:8000](http://localhost:8000)

## Description about various files:
- **app/static/chat.html**: HTML file for the frontend chat interface.
- **app/static/chatbot.js**: JavaScript file handling frontend logic.
- **app/.env**: Contains Hugging Face API key used for generation.
- **app/config.py**: Sets API keys for callback.
- **app/embedding.py**: Embeds input text into vector form using `all-MiniLM-L6-v2`.
- **app/main.py**: Entry point of the FastAPI app; handles routing and endpoints.
- **app/rag_chain.py**: Combines the retriever and generator into a complete RAG chain.
- **app/retriever.py**: Handles document retrieval using semantic similarity.
- **app/st.py**: Streamlit based UI.
- **app/vector_store.py**: Initializes and manages the FAISS vector index.
- **data/documents.json**: Contains the documents about Indium’s services that are used to answer user queries.
- **Pipfile**: Specifies the dependencies for the project.
- **Pipfile.lock**: Ensures consistent dependency versions.
- **requirements.txt**: Lists all top-level Python dependencies.