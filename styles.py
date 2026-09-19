"""
styles.py
Visual styling helpers for ContractLens.
Contains: inject_css() for global CSS, and small functions that return
ready-made HTML snippets (stat cards, badges, pills) used across pages.
Does not touch any backend logic.
"""

import streamlit as st


def inject_css():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');

        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }

        /* Hide Streamlit's default menu and footer */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}

        /* Sidebar: dark purple gradient */
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #3B1E7A 0%, #6C3EF4 100%);
        }
        section[data-testid="stSidebar"] * {
            color: #F3F0FF !important;
        }

        /* Logo card at top of sidebar */
        .logo-card {
            background: #FFFFFF;
            border-radius: 16px;
            padding: 18px 12px;
            text-align: center;
            margin-bottom: 6px;
            animation: fadeSlideUp 0.5s ease-out;
        }
        .logo-card .logo-emoji {
            font-size: 34px;
        }
        .logo-card .logo-text {
            color: #3B1E7A !important;
            font-weight: 800;
            font-size: 20px;
            margin-top: 4px;
        }

        @keyframes fadeSlideUp {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def logo_card(title: str = "ContractLens", emoji: str = "📄🔍") -> str:
    """Returns an HTML snippet for a white logo card, meant for the sidebar."""
    return f"""
    <div class="logo-card">
        <div class="logo-emoji">{emoji}</div>
        <div class="logo-text">{title}</div>
    </div>
    """


def stat_card(title: str, value: str, caption: str, gradient: str, icon: str) -> str:
    """Returns an HTML snippet for a colorful gradient stat card."""
    return f"""
    <div style="
        background: {gradient};
        border-radius: 14px;
        padding: 20px;
        color: white;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        animation: fadeSlideUp 0.5s ease-out;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    " onmouseover="this.style.transform='translateY(-4px)'; this.style.boxShadow='0 8px 20px rgba(0,0,0,0.15)';"
       onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 4px 12px rgba(0,0,0,0.08)';">
        <div style="font-size: 26px;">{icon}</div>
        <div style="font-size: 30px; font-weight: 800; margin-top: 6px;">{value}</div>
        <div style="font-size: 13px; opacity: 0.9; margin-top: 4px;">{title}</div>
        <div style="font-size: 12px; opacity: 0.75;">{caption}</div>
    </div>
    """


def risk_badge(severity: str) -> str:
    """Returns an HTML pill badge colored by severity: high=red, medium=amber, low=green."""
    colors = {
        "high": ("#FEE2E2", "#DC2626"),
        "medium": ("#FEF3C7", "#D97706"),
        "low": ("#D1FAE5", "#059669"),
    }
    bg, fg = colors.get(severity.lower(), ("#E5E7EB", "#374151"))
    return f"""
    <span style="
        background: {bg};
        color: {fg};
        padding: 4px 12px;
        border-radius: 999px;
        font-size: 12px;
        font-weight: 700;
        margin-right: 6px;
    ">{severity.upper()}</span>
    """


def source_pill(text: str) -> str:
    """Returns a small grey pill badge for a source citation."""
    return f"""
    <span style="
        background: #F3F4F6;
        color: #4B5563;
        padding: 3px 10px;
        border-radius: 999px;
        font-size: 11px;
        font-weight: 600;
    ">📌 {text}</span>
    """


def alert_card(count: int, label: str, color: str, pulse: bool = False) -> str:
    """Returns an HTML snippet for a small alert/metric card, optionally with a pulsing dot."""
    dot = ""
    if pulse and count > 0:
        dot = f"""
        <span style="
            display:inline-block;
            width:8px; height:8px;
            border-radius:50%;
            background:{color};
            margin-left:6px;
            animation: pulseDot 1.5s infinite;
        "></span>
        """
    return f"""
    <div style="
        background: white;
        border-radius: 14px;
        padding: 18px 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        animation: fadeSlideUp 0.5s ease-out;
    ">
        <div style="font-size: 28px; font-weight: 800; color: {color};">{count}{dot}</div>
        <div style="font-size: 13px; color: #6B7280; margin-top: 2px;">{label}</div>
    </div>
    <style>
    @keyframes pulseDot {{
        0% {{ opacity: 1; }}
        50% {{ opacity: 0.3; }}
        100% {{ opacity: 1; }}
    }}
    </style>
    """