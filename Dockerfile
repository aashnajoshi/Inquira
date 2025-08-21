FROM python:3.12-slim AS builder
WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir torch==2.3.0+cpu -f https://download.pytorch.org/whl/torch_stable.html \
    && pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir langchain-huggingface

ENV HF_HOME=/app/cache/hf_cache \
    TRANSFORMERS_CACHE=/app/cache/hf_cache \
    SENTENCE_TRANSFORMERS_HOME=/app/cache/st_cache

RUN mkdir -p /app/cache/hf_cache /app/cache/st_cache \
    && chmod -R 777 /app/cache \
    && python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-mpnet-base-v2')"

FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    HF_HOME=/app/cache/hf_cache \
    TRANSFORMERS_CACHE=/app/cache/hf_cache \
    SENTENCE_TRANSFORMERS_HOME=/app/cache/st_cache

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libopenblas-dev \
        libomp-dev && \
    rm -rf /var/lib/apt/lists/* \
    && mkdir -p /app/cache/hf_cache /app/cache/st_cache \
    && chmod -R 777 /app/cache

COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /app/cache /app/cache
COPY app/ ./app/
COPY data/ ./data/

RUN chmod +x /usr/local/bin/uvicorn

EXPOSE 7860
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
