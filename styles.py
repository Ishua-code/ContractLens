"""
styles.py
Visual styling helpers for ContractLens.
Contains: inject_css() for global CSS, and small functions that return
ready-made HTML snippets (stat cards, badges, pills) used across pages.
Does not touch any backend logic.
"""

import streamlit as st
import base64


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


import base64

def logo_card(title: str = "ContractLens", image_path: str = "logo_new.png") -> str:
    """Returns an HTML snippet for a white logo card with the real logo image, meant for the sidebar."""
    with open(image_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()
    return f"""
    <div class="logo-card">
        <img src="data:image/png;base64,{encoded}" style="width: 100%; max-width: 180px; margin: 0 auto; display: block;">
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
def tool_pill(text: str) -> str:
    """Returns a small purple pill badge for a 'tool used' label."""
    return f"""
    <span style="
        background: #EDE9FE;
        color: #6C3EF4;
        padding: 3px 10px;
        border-radius: 999px;
        font-size: 11px;
        font-weight: 700;
        margin-right: 6px;
        display: inline-block;
    ">🛠️ {text}</span>
    """


def compare_card(clause: str, change_type: str, impact: str, old: str, new: str, explanation: str) -> str:
    """Returns an HTML snippet for a Compare-page change card with a colored left border."""
    styles = {
        "increased": ("#EF4444", "#FEE2E2", "#DC2626", "🔴 Increased Risk"),
        "reduced": ("#22C55E", "#D1FAE5", "#059669", "🟢 Reduced Risk"),
        "neutral": ("#9CA3AF", "#F3F4F6", "#4B5563", "⚪ Neutral"),
    }
    border, badge_bg, badge_fg, badge_label = styles.get(impact.lower(), styles["neutral"])

    old_html = f'<span style="color:#9CA3AF; text-decoration: line-through;">{old}</span>' if old else '<span style="color:#9CA3AF;">(not present)</span>'
    new_html = f'<span style="color:#1F2937; font-weight:700;">{new}</span>' if new else '<span style="color:#9CA3AF;">(not present)</span>'

    return f"""
    <div style="
        background: white;
        border-left: 5px solid {border};
        border-radius: 14px;
        padding: 18px 20px;
        margin-bottom: 14px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        animation: fadeSlideUp 0.5s ease-out;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    " onmouseover="this.style.transform='translateY(-4px)'; this.style.boxShadow='0 8px 20px rgba(0,0,0,0.15)';"
       onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 2px 8px rgba(0,0,0,0.06)';">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap;">
            <div style="font-size:16px; font-weight:800; color:#1F2937;">{clause}</div>
            <span style="
                background:{badge_bg}; color:{badge_fg};
                padding:4px 12px; border-radius:999px;
                font-size:12px; font-weight:700;
            ">{badge_label}</span>
        </div>
        <div style="font-size:12px; color:#6B7280; margin-top:4px;">Change type: {change_type.capitalize()}</div>
        <div style="margin-top:12px; font-size:14px;"><b>Old:</b> {old_html}</div>
        <div style="margin-top:4px; font-size:14px;"><b>New:</b> {new_html}</div>
        <div style="margin-top:10px; font-size:13px; color:#4B5563;">💡 {explanation}</div>
    </div>
    """


def empty_state(message: str) -> str:
    """Returns an HTML snippet for a friendly empty-state message card."""
    return f"""
    <div style="
        background: white;
        border-radius: 14px;
        padding: 32px 24px;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        animation: fadeSlideUp 0.5s ease-out;
        margin-top: 12px;
    ">
        <div style="font-size: 15px; color: #4B5563; line-height: 1.6;">{message}</div>
        <div style="font-size: 22px; margin-top: 10px;">👈</div>
        <div style="font-size: 12px; color: #9CA3AF; margin-top: 4px;">Use the sidebar to explore</div>
    </div>
    """