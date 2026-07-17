import os
import json
import numpy as np
from typing import List, Dict, Any, Tuple
import google.generativeai as genai

FAISS_AVAILABLE = False
try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    pass

def chunk_text(text: str, chunk_size: int = 800, overlap: int = 150) -> List[str]:
    if not text:
        return []
    words = text.split()
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return [c.strip() for c in chunks if len(c.strip()) > 50]

def get_embedding(text: str, api_key: str) -> List[float]:
    try:
        genai.configure(api_key=api_key)
        response = genai.embed_content(
            model="models/text-embedding-004",
            content=text,
            task_type="retrieval_document"
        )
        return response["embedding"]
    except Exception as e:
        try:
            response = genai.embed_content(
                model="models/embedding-001",
                content=text,
                task_type="retrieval_document"
            )
            return response["embedding"]
        except Exception as ex:
            print(f"Embedding failed: {ex}")
            return [0.0] * 768

def create_index(chunks: List[str], file_name: str, api_key: str) -> str:
    embeddings = []
    for chunk in chunks:
        emb = get_embedding(chunk, api_key)
        embeddings.append(emb)
    index_data = {
        "file_name": file_name,
        "chunks": chunks,
        "embeddings": embeddings
    }
    os.makedirs("uploads", exist_ok=True)
    index_path = os.path.join("uploads", f"{file_name}_index.json")
    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(index_data, f)
    return index_path

def retrieve_context(query: str, file_name: str, api_key: str, top_k: int = 3) -> str:
    index_path = os.path.join("uploads", f"{file_name}_index.json")
    if not os.path.exists(index_path):
        return ""
    with open(index_path, "r", encoding="utf-8") as f:
        index_data = json.load(f)
    chunks = index_data["chunks"]
    embeddings = np.array(index_data["embeddings"])
    if len(embeddings) == 0 or len(chunks) == 0:
        return ""
    query_emb = np.array(get_embedding(query, api_key))
    if FAISS_AVAILABLE:
        try:
            d = embeddings.shape[1]
            index = faiss.IndexFlatIP(d)
            faiss.normalize_L2(embeddings)
            query_arr = query_emb.reshape(1, -1).astype('float32')
            faiss.normalize_L2(query_arr)
            index.add(embeddings.astype('float32'))
            distances, indices = index.search(query_arr, min(top_k, len(chunks)))
            retrieved_chunks = [chunks[i] for i in indices[0] if i >= 0]
            return "\n\n---\n\n".join(retrieved_chunks)
        except Exception as e:
            print(f"FAISS retrieval failed, falling back to numpy: {e}")
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    norms[norms == 0] = 1e-10
    norm_embeddings = embeddings / norms

    q_norm = np.linalg.norm(query_emb)
    if q_norm == 0:
        q_norm = 1e-10
    norm_query = query_emb / q_norm

    similarities = np.dot(norm_embeddings, norm_query)
    top_indices = np.argsort(similarities)[::-1][:top_k]
    retrieved_chunks = [chunks[i] for i in top_indices]
    return "\n\n---\n\n".join(retrieved_chunks)
