import streamlit as st
from constants import ARENA, TAUPE, MARRON, MARFIL


def apply_styles() -> None:
    """Inyecta el CSS de marca BEN AURA en la app."""
    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=Poppins:wght@400;500;600&display=swap');

        html, body, [class*="css"] {{
            font-family: 'Poppins', sans-serif;
        }}

        @keyframes baFadeInUp {{
            from {{ opacity: 0; transform: translateY(10px); }}
            to   {{ opacity: 1; transform: translateY(0); }}
        }}

        .main .block-container {{
            animation: baFadeInUp 0.4s ease-out;
        }}

        hr {{
            border: none;
            height: 2px;
            background: linear-gradient(90deg, {ARENA}, transparent);
            margin: 1.6rem 0;
        }}

        .stApp {{ background-color: var(--background-color); }}

        h1, h2, h3 {{
            color: var(--text-color);
            font-family: 'Playfair Display', 'Georgia', serif;
            letter-spacing: 0.3px;
        }}
        p, span, label, .stMarkdown {{ color: var(--text-color); }}

        h1 {{
            border-bottom: 3px solid {TAUPE};
            padding-bottom: 10px;
            margin-bottom: 18px !important;
        }}

        /* --- Sidebar --- */
        [data-testid="stSidebar"] {{
            background: linear-gradient(180deg, {MARRON} 0%, #5A4939 100%);
        }}
        [data-testid="stSidebar"] * {{
            color: {MARFIL} !important;
            font-family: 'Poppins', sans-serif;
        }}
        [data-testid="stSidebar"] h1 {{
            font-family: 'Playfair Display', serif;
            border-bottom: none;
            font-size: 1.8rem;
        }}
        [data-testid="stSidebar"] [role="radiogroup"] label {{
            background-color: rgba(255,255,255,0.06);
            border-radius: 10px;
            padding: 10px 12px;
            margin-bottom: 6px;
            transition: all 0.2s ease;
            border-left: 3px solid transparent;
        }}
        [data-testid="stSidebar"] [role="radiogroup"] label:hover {{
            background-color: rgba(255,255,255,0.16);
            border-left: 3px solid {ARENA};
            transform: translateX(2px);
        }}
        [data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) {{
            background-color: rgba(255,255,255,0.22);
            border-left: 3px solid {ARENA};
        }}

        /* --- Tarjetas de métricas --- */
        [data-testid="stMetric"] {{
            background-color: var(--secondary-background-color);
            border: 1px solid var(--secondary-background-color);
            border-top: 3px solid {TAUPE};
            border-radius: 14px;
            padding: 16px 18px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.06);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
            animation: baFadeInUp 0.5s ease-out;
        }}
        [data-testid="stMetric"]:hover {{
            transform: translateY(-3px);
            box-shadow: 0 6px 18px rgba(0,0,0,0.12);
        }}
        [data-testid="stMetricLabel"] {{ color: var(--text-color); opacity: 0.75; font-weight: 500; }}
        [data-testid="stMetricValue"] {{ color: var(--text-color); font-family: 'Playfair Display', serif; }}

        /* --- Botones --- */
        div.stButton > button, .stFormSubmitButton > button {{
            background: linear-gradient(135deg, {MARRON} 0%, {TAUPE} 100%);
            color: white;
            border: none;
            border-radius: 24px;
            padding: 8px 22px;
            font-weight: 600;
            box-shadow: 0 2px 8px rgba(111,91,71,0.35);
            transition: all 0.2s ease;
        }}
        div.stButton > button:hover, .stFormSubmitButton > button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 16px rgba(111,91,71,0.45);
            color: white;
        }}

        /* --- Inputs --- */
        div[data-baseweb="select"] > div,
        div[data-baseweb="input"] > div,
        div[data-baseweb="base-input"] {{
            border-radius: 10px !important;
            min-height: 42px;
            transition: border-color 0.2s ease, box-shadow 0.2s ease;
        }}
        div[data-baseweb="select"] > div:focus-within,
        div[data-baseweb="input"] > div:focus-within {{
            border-color: {TAUPE} !important;
            box-shadow: 0 0 0 2px rgba(166,143,117,0.25) !important;
        }}
        ul[data-testid="stSelectboxVirtualDropdown"] li {{
            white-space: normal;
        }}

        /* --- Tablas --- */
        [data-testid="stDataFrame"] {{
            border: 1px solid var(--secondary-background-color);
            border-radius: 14px;
            overflow: hidden;
            box-shadow: 0 2px 10px rgba(0,0,0,0.06);
        }}

        /* --- Formularios --- */
        [data-testid="stForm"] {{
            border: 1px solid var(--secondary-background-color);
            border-radius: 16px;
            padding: 20px;
            background-color: var(--secondary-background-color);
            box-shadow: 0 4px 16px rgba(0,0,0,0.08);
            animation: baFadeInUp 0.5s ease-out;
        }}
        </style>
    """, unsafe_allow_html=True)
