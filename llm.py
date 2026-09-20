import os
import re
import json
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types, errors


load_dotenv()

client = client = genai.Client(api_key=_get_key())

# Model can be changed from .env without touching code
MODEL = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")
# Optional backup model, used if the main one stays overloaded (503)
FALLBACK_MODEL = os.getenv("GEMINI_FALLBACK_MODEL")

MAX_ATTEMPTS = 6


def generate_with_retry(**kwargs):
    """Call Gemini. Waits and retries on rate limits (429) and overload (503/500).
    If GEMINI_FALLBACK_MODEL is set, switches to it after 3 failed attempts."""
    for attempt in range(MAX_ATTEMPTS):
        # After 3 failures, switch to the fallback model (if one is set)
        if attempt == 3 and FALLBACK_MODEL and kwargs.get("model") != FALLBACK_MODEL:
            print(f"Switching to fallback model: {FALLBACK_MODEL}")
            kwargs["model"] = FALLBACK_MODEL
        try:
            return client.models.generate_content(**kwargs)
        except (errors.ClientError, errors.ServerError) as e:
            msg = str(e)
            if "429" in msg:
                m = re.search(r"retry in ([\d.]+)s", msg)
                wait = float(m.group(1)) + 2 if m else 30
                print(f"Rate limit hit, waiting {wait:.0f}s (attempt {attempt + 1}/{MAX_ATTEMPTS})...")
                time.sleep(wait)
            elif "503" in msg or "500" in msg or "UNAVAILABLE" in msg:
                wait = 5 * (attempt + 1)
                print(f"Model busy (503), waiting {wait}s (attempt {attempt + 1}/{MAX_ATTEMPTS})...")
                time.sleep(wait)
            else:
                raise  # 404, invalid key, etc: do not retry
    raise RuntimeError("Gemini still unavailable after all retries")


def ask_llm(prompt, json_mode=False, system=None):
    config = types.GenerateContentConfig(
        system_instruction=system,
        response_mime_type="application/json" if json_mode else None,
        temperature=0.2,
    )
    response = generate_with_retry(model=MODEL, contents=prompt, config=config)
    text = response.text
    return json.loads(text) if json_mode else text


if __name__ == "__main__":
    print(ask_llm("Say hello in one sentence."))