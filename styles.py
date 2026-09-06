import streamlit as st
from constants import (
    FONDO_APP, TEXTO_DARK, TEXTO_MUTED, BORDE_LIGHT,
    CARD_BG, PRIMARY, ACCENT,
)


def apply_styles() -> None:
    """Inyecta un diseño Clean SaaS / Minimalista Moderno (estilo Stripe/Notion)."""
    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

        html, body, [class*="css"], .stApp {{
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
            background-color: {FONDO_APP} !important;
            color: {TEXTO_DARK} !important;
        }}

        /* Contenedor principal con espaciado prolijo */
        .main .block-container {{
            max-width: 1200px;
            padding-top: 2rem;
            padding-bottom: 3rem;
        }}

        /* Divisores discretos */
        hr {{
            border: none;
            height: 1px;
            background: {BORDE_LIGHT};
            margin: 2rem 0;
        }}

        /* Tipografía de títulos moderna y sobria */
        h1, h2, h3, h4 {{
            font-family: 'Plus Jakarta Sans', sans-serif !important;
            font-weight: 700 !important;
            letter-spacing: -0.025em !important;
            color: {TEXTO_DARK} !important;
        }}

        h1 {{
            font-size: 1.85rem !important;
            border-bottom: none !important;
            padding-bottom: 0 !important;
            margin-bottom: 1.25rem !important;
        }}

        h2 {{
            font-size: 1.4rem !important;
            margin-top: 1rem !important;
            margin-bottom: 0.75rem !important;
        }}

        h3 {{
            font-size: 1.15rem !important;
            font-weight: 600 !important;
        }}

        p, span, label, .stMarkdown {{
            color: {TEXTO_DARK};
        }}

        /* Subtítulos y captions en gris neutro */
        .stCaption, [data-testid="stCaptionContainer"] {{
            color: {TEXTO_MUTED} !important;
            font-size: 0.875rem !important;
        }}

        /* --- SIDEBAR MINIMALISTA --- */
        [data-testid="stSidebar"] {{
            background-color: #FFFFFF !important;
            border-right: 1px solid {BORDE_LIGHT} !important;
        }}
        [data-testid="stSidebar"] * {{
            color: {TEXTO_DARK} !important;
        }}
        [data-testid="stSidebar"] h1 {{
            font-size: 1.3rem !important;
            font-weight: 700 !important;
            letter-spacing: -0.02em;
            margin-bottom: 0.25rem !important;
        }}
        [data-testid="stSidebar"] [role="radiogroup"] {{
            gap: 4px;
        }}
        [data-testid="stSidebar"] [role="radiogroup"] label {{
            background-color: transparent !important;
            border-radius: 8px !important;
            padding: 8px 14px !important;
            margin-bottom: 2px !important;
            transition: all 0.15s ease-in-out !important;
            border: 1px solid transparent !important;
            cursor: pointer;
            font-size: 0.92rem !important;
            font-weight: 500 !important;
        }}
        /* Ocultar círculo de radio nativo */
        [data-testid="stSidebar"] [role="radiogroup"] label > div:first-child {{
            display: none !important;
        }}
        [data-testid="stSidebar"] [role="radiogroup"] label:hover {{
            background-color: #F1F5F9 !important;
            transform: none !important;
        }}
        [data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) {{
            background-color: #F1F5F9 !important;
            color: {PRIMARY} !important;
            font-weight: 600 !important;
            border: 1px solid {BORDE_LIGHT} !important;
        }}

        /* --- CARDS DE MÉTRICAS (Clean SaaS) --- */
        [data-testid="stMetric"] {{
            background-color: {CARD_BG} !important;
            border: 1px solid {BORDE_LIGHT} !important;
            border-top: 1px solid {BORDE_LIGHT} !important;
            border-radius: 12px !important;
            padding: 18px 20px !important;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04) !important;
            transition: border-color 0.15s ease, box-shadow 0.15s ease !important;
        }}
        [data-testid="stMetric"]:hover {{
            border-color: #CBD5E1 !important;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05) !important;
            transform: none !important;
        }}
        [data-testid="stMetricLabel"] {{
            color: {TEXTO_MUTED} !important;
            font-size: 0.85rem !important;
            font-weight: 500 !important;
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }}
        [data-testid="stMetricValue"] {{
            color: {TEXTO_DARK} !important;
            font-family: 'Plus Jakarta Sans', sans-serif !important;
            font-weight: 700 !important;
            font-size: 1.85rem !important;
            letter-spacing: -0.03em;
        }}

        /* --- BOTONES MODERNOS --- */
        div.stButton > button, .stFormSubmitButton > button {{
            background: {PRIMARY} !important;
            color: #FFFFFF !important;
            border: 1px solid {PRIMARY} !important;
            border-radius: 8px !important;
            padding: 8px 18px !important;
            font-weight: 600 !important;
            font-size: 0.9rem !important;
            letter-spacing: -0.01em;
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05) !important;
            transition: all 0.15s ease-in-out !important;
        }}
        div.stButton > button:hover, .stFormSubmitButton > button:hover {{
            background: #334155 !important;
            border-color: #334155 !important;
            color: #FFFFFF !important;
            transform: translateY(-1px) !important;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.08) !important;
        }}

        /* --- INPUTS & SELECTS --- */
        div[data-baseweb="select"] > div,
        div[data-baseweb="input"] > div,
        div[data-baseweb="base-input"],
        div[data-baseweb="textarea"] > div {{
            border-radius: 8px !important;
            border: 1px solid {BORDE_LIGHT} !important;
            background-color: #FFFFFF !important;
            min-height: 40px;
            transition: border-color 0.15s ease, box-shadow 0.15s ease;
        }}
        div[data-baseweb="select"] > div:focus-within,
        div[data-baseweb="input"] > div:focus-within,
        div[data-baseweb="textarea"] > div:focus-within {{
            border-color: {PRIMARY} !important;
            box-shadow: 0 0 0 3px rgba(30, 41, 59, 0.1) !important;
        }}

        /* --- TABLAS --- */
        [data-testid="stDataFrame"] {{
            border: 1px solid {BORDE_LIGHT} !important;
            border-radius: 10px !important;
            overflow: hidden;
            background-color: #FFFFFF !important;
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03) !important;
        }}

        /* --- FORMULARIOS --- */
        [data-testid="stForm"] {{
            border: 1px solid {BORDE_LIGHT} !important;
            border-radius: 12px !important;
            padding: 24px !important;
            background-color: #FFFFFF !important;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04) !important;
        }}

        /* Pestañas (Tabs) estilo moderno */
        button[data-baseweb="tab"] {{
            font-weight: 500 !important;
            font-size: 0.92rem !important;
            padding: 10px 16px !important;
            border-radius: 6px 6px 0 0 !important;
        }}
        button[data-baseweb="tab"][aria-selected="true"] {{
            color: {PRIMARY} !important;
            font-weight: 700 !important;
            border-bottom: 2px solid {PRIMARY} !important;
        }}
        </style>
    """, unsafe_allow_html=True)
