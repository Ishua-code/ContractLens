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
    st.info("Coming soon — this page will be built in the next task.")

elif page == "Chat":
    st.title("💬 Chat with your Contract")
    st.info("Coming soon — this page will be built in a later task.")

elif page == "Compare":
    st.title("🔍 Compare Contract Versions")
    st.info("Coming soon — this page will be built in a later task.")