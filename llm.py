import os
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODEL = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")


def ask_llm(prompt, json_mode=False, system=None):
    config = types.GenerateContentConfig(
        system_instruction=system,
        response_mime_type="application/json" if json_mode else None,
        temperature=0.2,
    )
    response = client.models.generate_content(
        model=MODEL, contents=prompt, config=config
    )
    text = response.text
    return json.loads(text) if json_mode else text


if __name__ == "__main__":
    print(ask_llm("Say hello in one sentence."))