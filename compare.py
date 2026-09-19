from llm import ask_llm

SYSTEM = """You are a careful contract analyst comparing two versions of the same contract.
Return ONLY a JSON array. Each item must have exactly these keys:
- "clause": the clause number or heading (for example "Clause 4.2")
- "change_type": one of "added", "removed", "modified"
- "old": the old wording (short), or null if the clause was added
- "new": the new wording (short), or null if the clause was removed
- "risk_impact": one of "increased", "reduced", "neutral"
- "explanation": one short sentence on why the risk changed for the customer
Only list real differences. Ignore formatting and whitespace changes.
If the two versions are identical, return an empty array [].
You assist human reviewers. You do not give legal advice."""


def compare_versions(text_a, text_b, retries=3):
    prompt = f"VERSION 1:\n{text_a}\n\nVERSION 2:\n{text_b}"
    last_error = None
    for _ in range(retries):
        try:
            data = ask_llm(prompt, json_mode=True, system=SYSTEM)
            if isinstance(data, dict):
                data = data.get("changes", [])
            if not isinstance(data, list):
                raise ValueError("Model did not return a JSON array")
            return data
        except Exception as e:
            last_error = e
    raise RuntimeError(f"Comparison failed after {retries} tries: {last_error}")


if __name__ == "__main__":
    import json
    a = open("sample_contracts/test.txt", encoding="utf-8").read()
    b = (a.replace("60 days written notice", "120 days written notice")
          .replace("5% fee", "10% fee")
          .replace("one month of fees", "one week of fees"))
    print(json.dumps(compare_versions(a, b), indent=2))