from llm import ask_llm
from deadlines import build_timeline, get_upcoming

SYSTEM = """You write a concise one-page contract summary for busy business stakeholders.
Use plain English and Markdown. Use ONLY the data provided. Never invent facts.
Structure:
## Overview (parties, term, one-sentence purpose)
## Key dates (effective, expiry, notice deadline)
## Money (payment terms, late fees)
## Top risks (max 3, with severity and clause)
## Action items (what to do and by when)
Cite the clause for every fact, for example (Clause 4.2).
End with: "This summary assists human review and is not legal advice." """


def summarize_contract(contract):
    data = {k: v for k, v in contract.items() if k != "full_text"}
    events = get_upcoming(build_timeline([contract]), 120)
    prompt = f"CONTRACT DATA:\n{data}\n\nUPCOMING EVENTS:\n{events}"
    return ask_llm(prompt, system=SYSTEM)


if __name__ == "__main__":
    import json
    with open("data/mock_result.json", encoding="utf-8") as f:
        mock = json.load(f)
    print(summarize_contract(mock))