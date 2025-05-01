import os

llm_config = {
    "config_list": [
        {
            "model": "llama3.1:8b",  # Ollama model
            "base_url": "http://localhost:11434",
            "api_key": "NotRequired",
            "price": [0, 0],
        },
        {
            "model": "gpt-4",
            "api_key": os.environ['OPENAI_API_KEY'],
        }
    ],
    "cache_seed": None,
}