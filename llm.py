import os
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types
import time
import re
from google.genai import errors

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODEL = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")


def ask_llm(prompt, json_mode=False, system=None):
    config = types.GenerateContentConfig(
        system_instruction=system,
        response_mime_type="application/json" if json_mode else None,
        temperature=0.2,
    )
    response = generate_with_retry(model=MODEL, contents=prompt, config=config)
    text = response.text
    return json.loads(text) if json_mode else text


def generate_with_retry(**kwargs):
    """Call Gemini and wait/retry when the free-tier rate limit (429) is hit."""
    for _ in range(4):
        try:
            return client.models.generate_content(**kwargs)
        except errors.ClientError as e:
            if "429" in str(e):
                m = re.search(r"retry in ([\d.]+)s", str(e))
                time.sleep(float(m.group(1)) + 2 if m else 30)
            else:
                raise
    raise RuntimeError("Rate limit: still exhausted after 4 retries")


if __name__ == "__main__":
    print(ask_llm("Say hello in one sentence."))


