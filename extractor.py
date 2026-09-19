import json
import re
from llm import ask_llm

SCHEMA = """{
  "contract_name": "string",
  "parties": ["string"],
  "effective_date": "YYYY-MM-DD or null",
  "expiration_date": "YYYY-MM-DD or null",
  "renewal_terms": {"text": "string", "auto_renew": true, "notice_days": 60, "source": "Clause X"},
  "payment_terms": {"text": "string", "source": "Clause X"},
  "termination": [{"text": "string", "source": "Clause X"}],
  "obligations": [{"party": "string", "text": "string", "deadline": "YYYY-MM-DD or null", "source": "Clause X"}],
  "risk_flags": [{"clause": "Clause X", "reason": "string", "severity": "low|medium|high"}]
}"""

SYSTEM = f"""You are a careful contract analyst. Return ONLY valid JSON matching this schema:
{SCHEMA}

Rules:
- For every item, set "source" to the exact clause number or section heading as written in the contract.
- If information is missing, use null. Never invent information.
- Dates must be YYYY-MM-DD.
- Flag risky clauses in risk_flags with a short reason and a severity of low, medium or high.
  Examples: auto-renewal, short notice windows, unlimited or very low liability caps,
  one-sided termination, high penalties or late fees, unusual indemnities.
- You assist human reviewers. You do not give legal advice."""


def _source_exists(source, text):
    """Check the cited clause label actually appears in the contract text."""
    if not source:
        return False
    nums = re.findall(r"\d+(?:\.\d+)*", str(source))
    if nums:
        return any(n in text for n in nums)
    return str(source).lower() in text.lower()


def _validate_sources(data, text):
    """Mark every cited source as verified or not, so the UI can show it."""
    def mark(item):
        if isinstance(item, dict) and "source" in item:
            item["source_verified"] = _source_exists(item["source"], text)

    mark(data.get("renewal_terms"))
    mark(data.get("payment_terms"))
    for key in ("termination", "obligations"):
        for item in data.get(key) or []:
            mark(item)
    for flag in data.get("risk_flags") or []:
        if isinstance(flag, dict):
            flag["source_verified"] = _source_exists(flag.get("clause"), text)
    return data


def extract_contract(text, name="contract", retries=3):
    prompt = f"Contract name: {name}\n\nCONTRACT TEXT:\n{text}"
    last_error = None
    for _ in range(retries):
        try:
            data = ask_llm(prompt, json_mode=True, system=SYSTEM)
            if not isinstance(data, dict):
                raise ValueError("Model did not return a JSON object")
            data["contract_name"] = name
            data["full_text"] = text
            return _validate_sources(data, text)
        except Exception as e:  # bad JSON, rate limit, etc.
            last_error = e
    raise RuntimeError(f"Extraction failed after {retries} tries: {last_error}")


if __name__ == "__main__":
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else "sample_contracts/test.txt"
    with open(path, encoding="utf-8") as f:
        result = extract_contract(f.read(), name=path)
    print(json.dumps(result, indent=2))