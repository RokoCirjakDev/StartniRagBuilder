import os
import requests
from dotenv import load_dotenv
from google import genai
from google.genai import types
from tools.local import call_local
load_dotenv()


def call_ai(prompt: str, LOCAL: bool):
    if(LOCAL):
        return call_local(prompt)
    else:
        try:
            client = genai.Client()
            response = client.models.generate_content(
                model="gemini-2.5-flash", contents=prompt,
                config=types.GenerateContentConfig(
                    thinking_config=types.ThinkingConfig(thinking_budget=0)
                ),
            )
            return response
        except Exception as e:
            print(f"Problem s Gemini API: {e}")
            return None