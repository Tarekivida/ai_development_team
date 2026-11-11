import os

llama3_8b_config = {
    "model": "llama3.1:8b",  # Ollama model
    "base_url": "http://localhost:11434",
    "api_key": "NotRequired",
    "price": [0, 0],
}

llama3_3b_config = {
    "model": "llama3.1:3b",  # Ollama model
    "base_url": "http://localhost:11434",
    "api_key": "NotRequired",
    "price": [0, 0],
}

qwen_7b_config = {
    "model": "qwen:7b-q4_K_M",  # Ollama model
    "base_url": "http://localhost:11434",
    "api_key": "NotRequired",
    "price": [0, 0],
}

gpt4_config = {
    "model": "gpt-4",
    "api_key": os.environ['OPENAI_API_KEY'],
}

llm_config = {
    "config_list": [
        llama3_8b_config,
        llama3_3b_config,
        qwen_7b_config,
        gpt4_config,
    ],
    "cache_seed": None,
}