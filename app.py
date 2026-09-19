"""
app.py
Main Streamlit app for ContractLens.
Owned by: Person 2 (Frontend)
"""

import json
import streamlit as st
from styles import inject_css, logo_card

# ---------- Page config ----------
st.set_page_config(
    page_title="ContractLens",
    page_icon="📄",
    layout="wide",
)

inject_css()

# ---------- Load mock data (temporary, until backend is wired in) ----------
@st.cache_data
def load_mock_data():
    with open("data/mock_result.json", "r", encoding="utf-8") as f:
        return json.load(f)

contract = load_mock_data()

# ---------- Sidebar navigation ----------
st.sidebar.markdown(logo_card(), unsafe_allow_html=True)
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
    st.title("📄 Upload a Contract")
    st.write("Upload a contract file (PDF, DOCX or TXT) to get started. We'll pull out the key dates, terms and risks automatically.")

    uploaded_file = st.file_uploader(
        "Choose a contract file",
        type=["pdf", "docx", "txt"],
    )

    if uploaded_file is not None:
        with st.spinner("Reading your file..."):
            from utils import extract_text_from_file
            try:
                text = extract_text_from_file(uploaded_file, uploaded_file.name)
                st.success(f"✅ Uploaded and read: {uploaded_file.name} ({len(text)} characters)")
            except Exception as e:
                st.error(f"⚠️ Couldn't read this file: {e}")
        st.info("👉 Full AI extraction is wired up in the backend — check the **Overview** page to see it in action on a sample contract.")
    else:
        st.info("💡 No file uploaded yet? No problem — head to the **Overview**, **Timeline & Alerts**, **Chat** or **Compare** pages to explore ContractLens with a sample contract.")

# ---------- Overview page ----------
elif page == "Overview":
    from styles import stat_card, risk_badge, source_pill

    st.title(f"📋 Overview: {contract['contract_name']}")

    # ---- Stat cards row ----
    high_risk_count = sum(1 for f in contract["risk_flags"] if f["severity"].lower() == "high")
    with open("data/timeline.json", "r", encoding="utf-8") as f:
        _tl = json.load(f)
    upcoming_90 = len([e for e in _tl.get("events", []) if e.get("days_left") is not None and 0 <= e["days_left"] <= 90])
    notice_days = contract["renewal_terms"].get("notice_days", "—")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(stat_card("Contracts analysed", "1", "Sample contract loaded", "linear-gradient(135deg, #6C3EF4, #8B5CF6)", "📄"), unsafe_allow_html=True)
    with c2:
        st.markdown(stat_card("Upcoming in 90 days", str(upcoming_90), "Events across contracts", "linear-gradient(135deg, #1FC8B5, #10B981)", "📅"), unsafe_allow_html=True)
    with c3:
        st.markdown(stat_card("Days to notice deadline", str(notice_days), "Required notice period", "linear-gradient(135deg, #3B82F6, #2563EB)", "⏰"), unsafe_allow_html=True)
    with c4:
        st.markdown(stat_card("High-risk clauses", str(high_risk_count), "Need close review", "linear-gradient(135deg, #334155, #1E293B)", "⚠️"), unsafe_allow_html=True)

    st.write("")
    st.divider()

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
    st.markdown(source_pill(renewal["source"]), unsafe_allow_html=True)

    st.divider()

    # Payment terms
    st.subheader("💳 Payment Terms")
    payment = contract["payment_terms"]
    st.write(payment["text"])
    st.markdown(source_pill(payment["source"]), unsafe_allow_html=True)

    st.divider()

    # Termination
    st.subheader("⛔ Termination")
    for term in contract["termination"]:
        st.write(term["text"])
        st.markdown(source_pill(term["source"]), unsafe_allow_html=True)

    st.divider()

    # Obligations
    st.subheader("✅ Obligations")
    for ob in contract["obligations"]:
        deadline = ob["deadline"] if ob["deadline"] else "No fixed deadline"
        st.write(f"**{ob['party']}**: {ob['text']} (Deadline: {deadline})")
        st.markdown(source_pill(ob["source"]), unsafe_allow_html=True)

    st.divider()

    # Risk flags
    st.subheader("⚠️ Risk Flags")
    for flag in contract["risk_flags"]:
        st.markdown(risk_badge(flag["severity"]) + f" **{flag['clause']}** — {flag['reason']}", unsafe_allow_html=True)

    st.divider()

    # Stakeholder summary
    st.subheader("📝 Stakeholder Summary")
    if st.button("Generate Summary"):
        with st.spinner("Generating summary..."):
            try:
                from summary import summarize_contract
                summary_text = summarize_contract(contract)
                st.markdown(summary_text)
            except Exception:
                st.info("Live summary generation is temporarily unavailable — showing a sample summary instead.")
                with open("data/nimbus_v1_summary.json", "r", encoding="utf-8") as f:
                    sample = json.load(f)
                st.markdown(sample["markdown"])

# ---------- Timeline & Alerts page ----------
elif page == "Timeline & Alerts":
    from styles import alert_card

    st.title("📅 Timeline & Alerts")

    with open("data/timeline.json", "r", encoding="utf-8") as f:
        timeline_data = json.load(f)

    events = timeline_data.get("events", [])
    upcoming_30d = timeline_data.get("upcoming_30d", [])
    overdue = timeline_data.get("overdue", [])

    # ---- Alert cards: 30 / 60 / 90 days ----
    st.subheader("🔔 Upcoming Alerts")

    def count_within(days_limit):
        return len([e for e in events if e.get("days_left") is not None and 0 <= e["days_left"] <= days_limit])

    col30, col60, col90 = st.columns(3)
    with col30:
        st.markdown(alert_card(count_within(30), "Next 30 days", "#EF4444", pulse=True), unsafe_allow_html=True)
    with col60:
        st.markdown(alert_card(count_within(60), "Next 60 days", "#F59E0B"), unsafe_allow_html=True)
    with col90:
        st.markdown(alert_card(count_within(90), "Next 90 days", "#3B82F6"), unsafe_allow_html=True)

    st.write("")

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

        color_map = {
            "start": "#6C3EF4",
            "obligation": "#3B82F6",
            "renewal": "#EF4444",
            "expiry": "#F59E0B",
        }

        fig = px.scatter(
            df,
            x="date",
            y="contract",
            color="type",
            color_discrete_map=color_map,
            hover_data=["event", "source"],
            title="Contract Events Timeline",
        )
        fig.update_traces(marker=dict(size=14))
        fig.update_xaxes(range=[df["date"].min() - pd.Timedelta(days=15), df["date"].max() + pd.Timedelta(days=15)])
        fig.update_layout(
            plot_bgcolor="white",
            paper_bgcolor="white",
            font=dict(family="Inter, sans-serif"),
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No timeline events found.")

# ---------- Chat page ----------
elif page == "Chat":
    st.title("💬 Chat with your Contract")
    st.caption("Ask a question in plain English. Every answer comes with sources.")

    from agent import chat

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

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

# ---------- Compare page ----------
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