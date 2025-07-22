import requests
import os
import re
import json

def call_local(prompt: str):
    url = "http://51.0.0.98:11434/api/chat"
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "model": "qwen3:14b",
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