import streamlit as st

from styles import apply_styles
from database import cargar_datos
from sections.inicio import render as render_inicio
from sections.nueva_venta import render as render_nueva_venta
from sections.productos import render as render_productos
from sections.clientes import render as render_clientes

# ── Configuración de página ───────────────────────────────
st.set_page_config(
    page_title="BEN AURA | Panel",
    page_icon="🕯️",
    layout="wide",
)
apply_styles()

# ── Sidebar de navegación ─────────────────────────────────
with st.sidebar:
    st.title("🕯️ BEN AURA")
    st.markdown("*Aromas que abrazan.*")
    st.divider()
    menu = st.radio(
        "Navegación",
        ["🏠 Inicio", "🛍️ Nueva Venta", "🕯️ Productos", "📲 Clientes"],
        label_visibility="collapsed",
    )

# ── Enrutamiento ──────────────────────────────────────────
df = cargar_datos()

if menu == "🏠 Inicio":
    render_inicio(df)

elif menu == "🛍️ Nueva Venta":
    render_nueva_venta()

elif menu == "🕯️ Productos":
    render_productos()

elif menu == "📲 Clientes":
    render_clientes(df)