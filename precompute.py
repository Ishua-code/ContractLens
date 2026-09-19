"""Run the backend once on sample contracts and save JSON to data/.
Usage: python precompute.py
Cost: 2 LLM calls per contract + 1 per v1/v2 pair.
"""
import json, dataclasses, datetime
from pathlib import Path

from extractor import extract_contract
from summary import summarize_contract
from compare import compare_versions
from deadlines import build_timeline, get_upcoming, get_overdue

SAMPLES = Path("data/samples")
OUT = Path("data")
OUT.mkdir(exist_ok=True)


def read_text(p: Path) -> str:
    if p.suffix.lower() == ".pdf":
        from pypdf import PdfReader
        return "\n".join((pg.extract_text() or "") for pg in PdfReader(str(p)).pages)
    if p.suffix.lower() == ".docx":
        import docx
        return "\n".join(par.text for par in docx.Document(str(p)).paragraphs)
    return p.read_text(encoding="utf-8")


def jsonable(o):
    if dataclasses.is_dataclass(o) and not isinstance(o, type):
        return {k: jsonable(v) for k, v in dataclasses.asdict(o).items()}
    if hasattr(o, "model_dump"):
        return jsonable(o.model_dump())
    if isinstance(o, dict):
        return {str(k): jsonable(v) for k, v in o.items()}
    if isinstance(o, (list, tuple, set)):
        return [jsonable(v) for v in o]
    if isinstance(o, (datetime.date, datetime.datetime)):
        return o.isoformat()
    if hasattr(o, "__dict__"):
        return jsonable(vars(o))
    return o


def save(name, obj):
    path = OUT / name
    path.write_text(json.dumps(jsonable(obj), indent=2, ensure_ascii=False), encoding="utf-8")
    print("saved", path)


def main():
    files = sorted(p for p in SAMPLES.glob("*") if p.suffix.lower() in {".txt", ".pdf", ".docx"})
    if not files:
        print(f"No contracts found in {SAMPLES}. Add some and re-run.")
        return

    texts, contracts = {}, []
    for p in files:
        texts[p.stem] = read_text(p)
        # skip if already computed, so re-runs don't burn quota
        cache = OUT / f"{p.stem}_summary.json"
        if cache.exists():
            print("skip (already done):", p.stem)
            continue
        print("extracting", p.stem)
        c = extract_contract(texts[p.stem], name=p.stem)
        save(f"{p.stem}_contract.json", c)
        print("summarizing", p.stem)
        s = summarize_contract(c)
        save(f"{p.stem}_summary.json", {"markdown": s} if isinstance(s, str) else s)
        contracts.append(c)

    if contracts:
        events = build_timeline(contracts)
        save("timeline.json", {
            "events": events,
            "upcoming_30d": get_upcoming(events, 30),
            "overdue": get_overdue(events),
        })

    for p in files:
        if p.stem.endswith("_v1") and (p.stem[:-3] + "_v2") in texts:
            base = p.stem[:-3]
            print("comparing", base)
            save(f"{base}_compare.json", compare_versions(texts[p.stem], texts[base + "_v2"]))


if __name__ == "__main__":
    main()