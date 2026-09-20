from datetime import date, datetime, timedelta


def _parse(d):
    if not d:
        return None
    try:
        return datetime.strptime(d, "%Y-%m-%d").date()
    except ValueError:
        return None


def build_timeline(contracts, today=None):
    """Return a sorted list of events across all contracts."""
    today = today or date.today()
    events = []

    def add(contract, event, d, etype, source=None, extra=None):
        if d is None:
            return
        item = {
            "contract": contract,
            "event": event,
            "date": d.isoformat(),
            "days_left": (d - today).days,
            "type": etype,
            "source": source,
        }
        if extra:
            item.update(extra)
        events.append(item)

    for c in contracts:
        name = c.get("contract_name", "contract")
        exp = _parse(c.get("expiration_date"))
        add(name, "Contract starts", _parse(c.get("effective_date")), "start")
        add(name, "Contract expires", exp, "expiry")

        renewal = c.get("renewal_terms") or {}
        notice_days = renewal.get("notice_days")
        if exp and renewal.get("auto_renew") and notice_days:
            notice_date = exp - timedelta(days=int(notice_days))
            add(
                name,
                f"Last day to give non-renewal notice ({notice_days} days before expiry)",
                notice_date,
                "renewal",
                renewal.get("source"),
                {"auto_renew": True, "expiry_date": exp.isoformat()},
            )

        for ob in c.get("obligations") or []:
            add(
                name,
                f"{ob.get('party')}: {ob.get('text')}",
                _parse(ob.get("deadline")),
                "obligation",
                ob.get("source"),
            )

    return sorted(events, key=lambda e: e["date"])


def get_upcoming(events, days=30):
    """Events from today up to `days` days ahead."""
    return [e for e in events if 0 <= e["days_left"] <= days]


def get_overdue(events):
    """Events whose date has already passed (excluding start events)."""
    return [e for e in events if e["days_left"] < 0 and e["type"] != "start"]


if __name__ == "__main__":
    import json
    with open("data/mock_result.json", encoding="utf-8") as f:
        mock = json.load(f)
    tl = build_timeline([mock])
    for e in tl:
        print(e["date"], e["days_left"], e["type"], "-", e["event"])
    print("Upcoming 90 days:", len(get_upcoming(tl, 90)))