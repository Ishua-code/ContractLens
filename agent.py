from google.genai import types
from llm import client, MODEL, generate_with_retry
from deadlines import build_timeline, get_upcoming

SYSTEM = """You are ContractLens, an assistant that helps people understand business contracts.
Always use the tools to look up facts before answering. Never guess.
Cite the clause number for every fact in your answer (for example: Clause 4.2).
If the tools do not return the answer, say you could not find it in the contracts.
You assist human reviewers. You do not give legal advice."""


def _clauses(contract):
    """Return a list of (clause_label, text) for one contract."""
    items = []
    full = contract.get("full_text")
    if full:
        import re
        parts = re.split(r"\n(?=\s*\d+(?:\.\d+)*\.?\s)", full)
        for p in parts:
            m = re.match(r"\s*(\d+(?:\.\d+)*)", p)
            if m:
                items.append((f"Clause {m.group(1)}", p.strip()))
    else:
        for key in ("renewal_terms", "payment_terms"):
            it = contract.get(key)
            if it:
                items.append((it.get("source"), it.get("text")))
        for key in ("termination", "obligations"):
            for it in contract.get(key) or []:
                items.append((it.get("source"), it.get("text")))
        for it in contract.get("risk_flags") or []:
            items.append((it.get("clause"), it.get("reason")))
    return items


def chat(question, contracts):
    """Answer a question about the contracts. Returns answer, sources, tools_used."""
    tools_used = []
    sources = []

    def search_clauses(query: str) -> list:
        """Search all contracts for clauses matching keywords in the query."""
        tools_used.append("search_clauses")
        words = [w.lower() for w in query.split() if len(w) > 2]
        results = []
        for c in contracts:
            for label, text in _clauses(c):
                score = sum(w in str(text).lower() for w in words)
                if score:
                    results.append((score, c.get("contract_name"), label, str(text)))
        results.sort(reverse=True)
        out = []
        for _, cname, label, text in results[:5]:
            sources.append(f"{cname} - {label}: {text[:200]}")
            out.append({"contract": cname, "clause": label, "text": text[:500]})
        return out

    def get_contract_field(contract_name: str, field: str) -> dict:
        """Get one field (parties, effective_date, expiration_date, renewal_terms,
        payment_terms, termination, obligations, risk_flags) of a contract by name."""
        tools_used.append("get_contract_field")
        for c in contracts:
            if contract_name.lower() in str(c.get("contract_name", "")).lower():
                value = c.get(field)
                sources.append(f"{c.get('contract_name')} - field: {field}")
                return {"value": value}
        return {"error": "contract not found"}

    def get_upcoming_deadlines(days: int) -> list:
        """List deadlines, renewals and expiries happening within the next N days."""
        tools_used.append("get_upcoming_deadlines")
        events = get_upcoming(build_timeline(contracts), days)
        for e in events:
            sources.append(f"{e['contract']} - {e['event']} ({e['date']})")
        return events

    def list_risk_flags() -> list:
        """List all risk flags across all contracts."""
        tools_used.append("list_risk_flags")
        flags = []
        for c in contracts:
            for f in c.get("risk_flags") or []:
                flags.append({"contract": c.get("contract_name"), **f})
                sources.append(f"{c.get('contract_name')} - {f.get('clause')}: {f.get('reason')}")
        return flags

    names = ", ".join(str(c.get("contract_name")) for c in contracts)
    config = types.GenerateContentConfig(
        system_instruction=SYSTEM,
        tools=[search_clauses, get_contract_field, get_upcoming_deadlines, list_risk_flags],
        temperature=0.2,
    )
    prompt = f"Available contracts: {names}\n\nQuestion: {question}"
    response = generate_with_retry(model=MODEL, contents=prompt, config=config)
    return {
        "answer": response.text,
        "sources": list(dict.fromkeys(sources)),
        "tools_used": list(dict.fromkeys(tools_used)),
    }


if __name__ == "__main__":
    import json
    import time
    with open("data/mock_result.json", encoding="utf-8") as f:
        mock = json.load(f)
    for q in ["When is the last day to cancel without renewing?",
              "What are the high risk clauses?"]:
        r = chat(q, [mock])
        print("Q:", q)
        print(json.dumps(r, indent=2))
        time.sleep(35)