import requests
import os
import re
import json
from config import config
import math 

def call_local(prompt: str):
    url = f"http://{config['ip']}:11434/api/chat"
    headers = {
        "Content-Type": "application/json"
    }

    if config["FAST_MODE"]:
        prompt = prompt + "/no_think"
    
    data = {
        "model": config["model"],
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "stream": False
    }
    
    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Problem s lokalnim API-jem: {e}")
        return None

def parse_local(response: json):
                stringresponse = response['message']['content']
                stringresponse = re.sub(r"<think>.*?</think>", "", stringresponse, flags=re.DOTALL).strip()
                return stringresponse

def get_embedding(text: str):
    url = f"http://{config['ip']}:11434/api/embeddings"
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "model": config["model_embedding"],
        "prompt": text
    }
    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        return response.json()['embedding']
    except requests.exceptions.RequestException as e:
        print(f"Problem with local embedding API: {e}")
        exit(1)

def get_embedding_safe(text: str):
    url = f"http://{config['ip']}:11434/api/embeddings"
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "model": config["model_embedding"],
        "prompt": text
    }

    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        raw_embedding = response.json().get('embedding', None)

        if not isinstance(raw_embedding, list):
            raise ValueError("API response 'embedding' is not a list")

        if len(raw_embedding) != 768:
            raise ValueError(f"Expected 1024 values, got {len(raw_embedding)}")

        clean_embedding = []
        for i, val in enumerate(raw_embedding):
            try:
                fval = float(val)
                if not math.isfinite(fval):
                    raise ValueError(f"Non-finite value at index {i}: {val}")
                clean_embedding.append(fval)
            except (ValueError, TypeError):
                raise ValueError(f"Invalid float at index {i}: {val}")

        return clean_embedding

    except requests.exceptions.RequestException as e:
        print(f"Problem with local embedding API: {e}")
        exit(1)
    except Exception as e:
        print(f"Embedding processing error: {e}")
        exit(1)