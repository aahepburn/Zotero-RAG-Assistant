# backend/local_llm.py
from typing import Optional
import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.2"  # change if you use a different local model

def generate_answer(prompt: str, max_tokens: int = 512, temperature: float = 0.3) -> str:
    """Generate answer with optimized parameters for academic RAG.
    
    Best practices:
    - max_tokens: 400-600 for detailed academic answers
    - temperature: 0.2-0.4 (low for factual accuracy, not too low to avoid repetition)
    - top_p: 0.9 for nucleus sampling (better than pure temperature)
    """
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "options": {
            "num_predict": max_tokens,
            "temperature": temperature,
            "top_p": 0.9,  # Nucleus sampling for better quality
            "repeat_penalty": 1.1,  # Slightly reduce repetition
            "top_k": 40,  # Standard top-k for academic text
        },
    }
    resp = requests.post(OLLAMA_URL, json=payload, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    return (data.get("response") or "").strip()
