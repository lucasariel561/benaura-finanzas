"""
📲 Clientes — CRM, historial de compras y enlace a WhatsApp
"""

import urllib.parse

import pandas as pd
import streamlit as st

from constants import format_currency
from database import cargar_datos


def _fmt(valor: float) -> str:
    return format_currency(valor)


def render(df: pd.DataFrame) -> None:
    st.header("📲 Clientes")

    if df.empty:
        st.info("Aún no hay clientes registrados.")
        return

    clientes_con_tel = df[df["telefono"].fillna("").str.strip() != ""]
    todos_clientes   = sorted(df["cliente"].dropna().unique().tolist())

    # Selector de cliente
    cliente_sel = st.selectbox("Seleccioná un cliente:", todos_clientes, key="crm_cliente")
    historial   = df[df["cliente"] == cliente_sel].sort_values("fecha", ascending=False)

    # ── Historial de compras ──────────────────────────────────
    st.subheader(f"📋 Historial de {cliente_sel}")
    total_cliente   = float(historial["total"].sum())
    ganancia_cliente = float(historial["ganancia"].sum())
    pedidos_cliente  = len(historial)

    c1, c2, c3 = st.columns(3)
    c1.metric("Pedidos totales",  pedidos_cliente)
    c2.metric("Total comprado",   _fmt(total_cliente))
    c3.metric("Ganancia generada", _fmt(ganancia_cliente))

    st.dataframe(
        historial[["fecha", "n_pedido", "producto", "cantidad", "total", "estado"]],
        use_container_width=True,
        hide_index=True,
        height=240,
    )

    # ── Mensaje de WhatsApp ───────────────────────────────────
    tel_rows = clientes_con_tel[clientes_con_tel["cliente"] == cliente_sel]["telefono"]
    if tel_rows.empty:
        st.warning("Este cliente no tiene teléfono registrado.")
        return

    tel = tel_rows.iloc[0]
    st.divider()
    st.subheader("💬 Enviar mensaje por WhatsApp")

    default_msg = f"¡Hola {cliente_sel}! Te compartimos las novedades de BEN AURA. ¡Te esperamos! 🕯️"
    template_key = f"crm_template_{cliente_sel}"
    if template_key not in st.session_state:
        st.session_state[template_key] = default_msg

    mensaje = st.text_area(
        "Podés editar el mensaje:",
        value=st.session_state[template_key],
        height=120,
        key=f"crm_texto_{cliente_sel}"
    )

    col_save, col_reset = st.columns([1, 1])
    if col_save.button("💾 Guardar plantilla", key="crm_guardar"):
        st.session_state[template_key] = mensaje
        st.success("Plantilla guardada.")

    if col_reset.button("↩️ Restaurar original", key="crm_reset"):
        st.session_state[template_key] = default_msg
        st.rerun()

    link = f"https://wa.me/{tel}?text={urllib.parse.quote(mensaje)}"
    st.markdown(
        f'<br><a href="{link}" target="_blank">'
        f'<button style="background:#25D366;color:white;padding:10px 24px;'
        f'border:none;border-radius:24px;font-weight:600;cursor:pointer;'
        f'font-size:15px;">Abrir WhatsApp Business 🚀</button></a>',
        unsafe_allow_html=True,
    )
