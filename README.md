# 📄 ContractLens

**Upload a contract. Know every deadline, obligation and risk in 60 seconds.**

Built for the Agentic AI Hackathon 2026.

---

## The Problem

Businesses handle contracts across vendors, customers and partners. Renewal dates, payment terms, termination clauses and obligations are buried in separate documents. Teams miss deadlines — like an auto-renewal notice date — or waste hours manually reading contracts to find a single clause.

## Our Solution

ContractLens is an AI-powered contract intelligence tool. Upload a contract and instantly get:

- **Structured extraction** — parties, effective/expiration dates, renewal terms, payment terms, termination conditions and obligations, each backed by a clause citation.
- **Risk flags** — colour-coded (🔴 high, 🟠 medium, 🟢 low) with a plain-English reason.
- **Notice deadline calculation** — our key innovation: automatically computes the last day to give non-renewal notice (expiry date minus notice period), so nothing slips through.
- **Obligation timeline** — a visual map of every contract's key dates and events.
- **Chat agent** — ask questions in plain English, get answers with sources and a "tools used" trail.
- **Version comparison** — upload two versions of a contract and see exactly what changed and how risk shifted.
- **Stakeholder summary** — a one-page, plain-English summary for non-lawyers.
- **Upcoming renewal alerts** — 30/60/90-day lookahead across all contracts.

ContractLens does not replace lawyers — it reduces the manual effort of reading and tracking contracts.

## Features

| Feature | Description |
|---|---|
| Upload | PDF, DOCX or TXT contracts |
| Overview | Parties, dates, terms, obligations, risk flags — all with source citations |
| Timeline & Alerts | Visual timeline of every contract event, plus 30/60/90-day alerts |
| Chat | Natural-language Q&A with sources and tools-used transparency |
| Compare | Side-by-side diff between two contract versions with risk impact |
| Stakeholder Summary | One-click plain-English summary for business stakeholders |

## Tech Stack

- **Frontend:** Streamlit, Plotly
- **AI:** Google Gemini API (`google-genai`)
- **File parsing:** pypdf, python-docx
- **Hosting:** Streamlit Community Cloud
- **Version control:** GitHub (feature branch → develop → main workflow)

## Architecture

Every AI-powered feature includes a graceful fallback to pre-computed sample data if the live API is temporarily unavailable, so the app never breaks mid-demo.

## Setup (local development)

1. Clone the repo:
2. Create and activate a virtual environment:
3. Install dependencies:
4. Add your Gemini API key in a .env file (never commit this):
5. Run the app:

## Live Demo

Live app link - coming soon

## Screenshots

Screenshots coming soon.

## Team

- **Backend / AI:** Person 1 - extraction, chat agent, comparison engine, deadline logic
- **Frontend / UX:** Person 2 - UI, sample data, deployment, demo video

## Disclaimer

ContractLens assists human review of contracts. It does not provide legal advice.