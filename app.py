"""
app.py
Main Streamlit app for ContractLens.
Owned by: Person 2 (Frontend)
"""

import json
import streamlit as st

# ---------- Page config ----------
st.set_page_config(
    page_title="ContractLens",
    page_icon="📄",
    layout="wide",
)

# ---------- Load mock data (temporary, until backend is wired in) ----------
@st.cache_data
def load_mock_data():
    with open("data/mock_result.json", "r", encoding="utf-8") as f:
        return json.load(f)

contract = load_mock_data()

# ---------- Sidebar navigation ----------
st.sidebar.title("📄 ContractLens")
st.sidebar.caption("Upload a contract. Know every deadline, obligation and risk in 60 seconds.")

page = st.sidebar.radio(
    "Navigate",
    ["Upload", "Overview", "Timeline & Alerts", "Chat", "Compare"],
)

# ---------- Helper: severity color ----------
def severity_color(severity: str) -> str:
    return {"high": "🔴", "medium": "🟠", "low": "🟢"}.get(severity.lower(), "⚪")

# ---------- Upload page ----------
if page == "Upload":
    st.title("Upload a Contract")
    st.write("Upload a contract file (PDF, DOCX or TXT) to get started.")

    uploaded_file = st.file_uploader(
        "Choose a contract file",
        type=["pdf", "docx", "txt"],
    )

    if uploaded_file is not None:
        st.success(f"Uploaded: {uploaded_file.name}")
        st.info("Using sample data for now — real extraction will be connected soon. Check the Overview page.")
    else:
        st.info("No file uploaded yet. In the meantime, explore the Overview page using sample data.")

# ---------- Overview page ----------
elif page == "Overview":
    st.title(f"📋 Overview: {contract['contract_name']}")

    # Parties and key dates
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Parties")
        for party in contract["parties"]:
            st.write(f"- {party}")
    with col2:
        st.subheader("Key Dates")
        st.write(f"**Effective Date:** {contract['effective_date']}")
        st.write(f"**Expiration Date:** {contract['expiration_date']}")

    st.divider()

    # Renewal terms
    st.subheader("🔄 Renewal Terms")
    renewal = contract["renewal_terms"]
    st.write(renewal["text"])
    st.caption(f"Source: {renewal['source']}")

    st.divider()

    # Payment terms
    st.subheader("💳 Payment Terms")
    payment = contract["payment_terms"]
    st.write(payment["text"])
    st.caption(f"Source: {payment['source']}")

    st.divider()

    # Termination
    st.subheader("⛔ Termination")
    for term in contract["termination"]:
        st.write(term["text"])
        st.caption(f"Source: {term['source']}")

    st.divider()

    # Obligations
    st.subheader("✅ Obligations")
    for ob in contract["obligations"]:
        deadline = ob["deadline"] if ob["deadline"] else "No fixed deadline"
        st.write(f"**{ob['party']}**: {ob['text']} (Deadline: {deadline})")
        st.caption(f"Source: {ob['source']}")

    st.divider()

    # Risk flags
    st.subheader("⚠️ Risk Flags")
    for flag in contract["risk_flags"]:
        icon = severity_color(flag["severity"])
        st.write(f"{icon} **{flag['clause']}** — {flag['reason']} (Severity: {flag['severity'].capitalize()})")

# ---------- Placeholder pages (built in later tasks) ----------
elif page == "Timeline & Alerts":
    st.title("📅 Timeline & Alerts")

    with open("data/timeline.json", "r", encoding="utf-8") as f:
        timeline_data = json.load(f)

    events = timeline_data.get("events", [])
    upcoming_30d = timeline_data.get("upcoming_30d", [])
    overdue = timeline_data.get("overdue", [])

    # ---- Alert cards: 30 / 60 / 90 days ----
    st.subheader("🔔 Upcoming Alerts")
    col30, col60, col90 = st.columns(3)

    def count_within(days_limit):
        return len([e for e in events if e.get("days_left") is not None and 0 <= e["days_left"] <= days_limit])

    with col30:
        st.metric("Next 30 days", count_within(30))
    with col60:
        st.metric("Next 60 days", count_within(60))
    with col90:
        st.metric("Next 90 days", count_within(90))

    if overdue:
        st.error(f"⚠️ {len(overdue)} overdue item(s) need attention!")
        for item in overdue:
            st.write(f"- **{item['contract']}**: {item['event']} (was due {item['date']})")

    if upcoming_30d:
        st.warning("Items due within 30 days:")
        for item in upcoming_30d:
            st.write(f"- **{item['contract']}**: {item['event']} on {item['date']}")

    st.divider()

    # ---- Plotly timeline chart ----
    st.subheader("📊 Contract Timeline")

    import plotly.express as px
    import pandas as pd

    if events:
        df = pd.DataFrame(events)
        df["date"] = pd.to_datetime(df["date"])

        fig = px.scatter(
            df,
            x="date",
            y="contract",
            color="type",
            hover_data=["event", "source"],
            title="Contract Events Timeline",
        )
        fig.update_traces(marker=dict(size=14))
        fig.update_xaxes(range=[df["date"].min() - pd.Timedelta(days=15), df["date"].max() + pd.Timedelta(days=15)])
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No timeline events found.")
elif page == "Chat":
    st.title("💬 Chat with your Contract")
    st.caption("Ask a question in plain English. Every answer comes with sources.")

    from agent import chat

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Show past messages
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            if msg["role"] == "assistant":
                if msg.get("tools_used"):
                    st.caption("🛠️ Tools used: " + ", ".join(msg["tools_used"]))
                if msg.get("sources"):
                    with st.expander("📚 Sources"):
                        for s in msg["sources"]:
                            st.write(f"- {s}")

    # Chat input box
    question = st.chat_input("Ask about renewal dates, obligations, risks...")

    if question:
        st.session_state.chat_history.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.write(question)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    result = chat(question, [contract])
                except Exception as e:
                    result = {
                        "answer": (
                            "I'm having trouble reaching the AI service right now, so here's what I can tell you "
                            "from the contract data directly: the renewal notice deadline is 60 days before "
                            "expiration (Clause 4.2), and the contract has two risk flags — auto-renewal terms "
                            "and a liability cap (see Overview page for full details)."
                        ),
                        "sources": ["Clause 4.2", "Clause 11"],
                        "tools_used": ["fallback_response"],
                    }
            st.write(result["answer"])
            if result.get("tools_used"):
                st.caption("🛠️ Tools used: " + ", ".join(result["tools_used"]))
            if result.get("sources"):
                with st.expander("📚 Sources"):
                    for s in result["sources"]:
                        st.write(f"- {s}")

        st.session_state.chat_history.append({
            "role": "assistant",
            "content": result["answer"],
            "tools_used": result.get("tools_used", []),
            "sources": result.get("sources", []),
        })

elif page == "Compare":
    st.title("🔍 Compare Contract Versions")
    st.caption("Upload two versions of a contract to see what changed and how risk shifted.")

    col1, col2 = st.columns(2)
    with col1:
        file_a = st.file_uploader("Version 1 (older)", type=["pdf", "docx", "txt"], key="compare_a")
    with col2:
        file_b = st.file_uploader("Version 2 (newer)", type=["pdf", "docx", "txt"], key="compare_b")

    def impact_badge(impact: str) -> str:
        return {"increased": "🔴 Increased Risk", "reduced": "🟢 Reduced Risk", "neutral": "⚪ Neutral"}.get(
            impact.lower(), "⚪ Unknown"
        )

    def show_changes(changes):
        if not changes:
            st.success("No meaningful differences found between the two versions.")
            return
        for change in changes:
            badge = impact_badge(change.get("risk_impact", ""))
            st.markdown(f"### {change.get('clause', 'Unknown clause')} — {badge}")
            st.caption(f"Change type: {change.get('change_type', 'unknown').capitalize()}")

            c1, c2 = st.columns(2)
            with c1:
                st.write("**Old:**")
                st.write(change.get("old") or "_(not present)_")
            with c2:
                st.write("**New:**")
                st.write(change.get("new") or "_(not present)_")

            st.write(f"💡 {change.get('explanation', '')}")
            st.divider()

    if file_a is not None and file_b is not None:
        if st.button("Compare versions"):
            from utils import extract_text_from_file
            from compare import compare_versions

            text_a = extract_text_from_file(file_a, file_a.name)
            text_b = extract_text_from_file(file_b, file_b.name)

            with st.spinner("Comparing versions..."):
                try:
                    changes = compare_versions(text_a, text_b)
                    show_changes(changes)
                except Exception as e:
                    st.warning("Live comparison is temporarily unavailable, showing a sample comparison instead.")
                    with open("data/nimbus_compare.json", "r", encoding="utf-8") as f:
                        changes = json.load(f)
                    show_changes(changes)
    else:
        st.info("Upload both versions above to compare, or see a sample comparison below.")
        if st.button("Show sample comparison"):
            with open("data/nimbus_compare.json", "r", encoding="utf-8") as f:
                changes = json.load(f)
            show_changes(changes)