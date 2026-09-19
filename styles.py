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

        /* Fade-slide-up animation for cards */
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