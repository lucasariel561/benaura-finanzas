"""
🏠 Inicio — Dashboard principal de BEN AURA
Incluye: métricas, gráfico de ganancias, tabla de pedidos,
edición de pedidos y gestión de entregas (antes pestaña separada).
"""

import time
import pandas as pd
import plotly.express as px
import streamlit as st

from constants import (
    MESES_ES, MARRON, TAUPE, ESTADOS_PEDIDO, MEDIOS_PAGO,
    normalizar_estado, format_currency,
)
from database import (
    cargar_datos, cargar_productos, eliminar_venta, actualizar_venta,
    actualizar_estado_pedido, obtener_producto_por_nombre,
    descontar_stock, restaurar_stock,
)


def _fmt(valor: float) -> str:
    return format_currency(valor)


def render(df: pd.DataFrame) -> None:
    st.header("🏠 Inicio")

    if df.empty:
        st.info("Aún no hay ventas registradas.")
        return

    # --- Preparar fechas y períodos ---
    df = df.copy()
    df["fecha"] = pd.to_datetime(df["fecha"])
    df["periodo"] = df["fecha"].dt.to_period("M")
    df["mes_anio"] = df["periodo"].apply(lambda p: f"{MESES_ES[p.month]} {p.year}")
    df["estado_display"] = df.apply(
        lambda r: normalizar_estado(str(r["estado"]), str(r.get("entrega", ""))), axis=1
    )

    periodos_ordenados = sorted(df["periodo"].unique())
    meses_disponibles  = [f"{MESES_ES[p.month]} {p.year}" for p in periodos_ordenados]

    mes_sel = st.selectbox(
        "📅 Filtrar por mes:",
        meses_disponibles,
        index=len(meses_disponibles) - 1,
        key="inicio_mes_sel",
    )

    df_mes = df[df["mes_anio"] == mes_sel]

    # --- Métricas principales ---
    ventas_mes      = float(df_mes["total"].sum())
    ganancia_mes    = float(df_mes["ganancia"].sum())
    pedidos_mes     = len(df_mes["n_pedido"].unique())
    ganancia_hist   = float(df["ganancia"].sum())

    # Tendencia vs mes anterior
    idx_actual = meses_disponibles.index(mes_sel)
    delta_str  = None
    if idx_actual > 0:
        mes_ant   = meses_disponibles[idx_actual - 1]
        gan_ant   = float(df[df["mes_anio"] == mes_ant]["ganancia"].sum())
        delta_raw = ganancia_mes - gan_ant
        # st.metric determina la flecha según si el string empieza con "-".
        # _fmt devuelve "$X.XXX,XX" (empieza con "$"), que Streamlit siempre
        # interpreta como positivo (↑). Hay que anteponer "-" explícitamente.
        delta_str = ("-" if delta_raw < 0 else "") + _fmt(abs(delta_raw))

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("💰 Ventas del mes",     _fmt(ventas_mes))
    c2.metric("📦 Pedidos del mes",    pedidos_mes)
    c3.metric("💵 Ganancia del mes",   _fmt(ganancia_mes), delta=delta_str)
    c4.metric("💎 Ganancia histórica", _fmt(ganancia_hist))

    st.divider()

    # --- Gráfico interactivo de ganancias mes a mes ---
    st.subheader("📈 Evolución de ganancias")
    df_agrup = (
        df.groupby("mes_anio")
        .agg(Ganancia=("ganancia", "sum"), Ingresos=("total", "sum"))
        .reindex([f"{MESES_ES[p.month]} {p.year}" for p in periodos_ordenados])
        .reset_index()
        .rename(columns={"mes_anio": "Mes"})
    )

    fig = px.bar(
        df_agrup,
        x="Mes",
        y="Ganancia",
        color_discrete_sequence=["#0F172A"],
        labels={"Ganancia": "Ganancia ($)", "Mes": ""},
        hover_data={"Ingresos": True},
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Plus Jakarta Sans, sans-serif", color="#475569"),
        margin=dict(l=0, r=0, t=10, b=0),
        bargap=0.45,
        bargroupgap=0.1,
        xaxis=dict(showgrid=False, tickfont=dict(size=12, color="#64748B")),
        yaxis=dict(gridcolor="#E2E8F0", tickfont=dict(size=12, color="#64748B")),
    )
    fig.update_traces(
        marker_line_width=0,
        marker_color="#1E293B",
        hovertemplate="<b>%{x}</b><br>Ganancia: $%{y:,.0f}<br>Ingresos: $%{customdata[0]:,.0f}<extra></extra>"
    )
    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # --- Stock bajo (alerta rápida) ---
    prods = cargar_productos()
    if not prods.empty:
        bajos = prods[prods["stock"] < 5]
        if not bajos.empty:
            nombres = ", ".join(bajos["nombre"].tolist())
            st.warning(f"⚠️ Stock bajo (menos de 5 unidades): **{nombres}**")

    # --- Tabla de pedidos del mes ---
    st.subheader(f"📋 Pedidos de {mes_sel}")
    st.caption("Seleccioná filas con el checkbox de la izquierda para eliminar.")

    cols_tabla = ["n_pedido", "fecha", "cliente", "producto",
                  "cantidad", "precio_unitario", "total", "estado_display"]
    df_tabla = df_mes.reset_index(drop=True)

    evento = st.dataframe(
        df_tabla[cols_tabla].rename(columns={"estado_display": "estado"}),
        use_container_width=True,
        hide_index=True,
        height=320,
        on_select="rerun",
        selection_mode="multi-row",
        key="tabla_ventas_inicio",
    )

    filas_sel = evento.selection.rows if evento and evento.selection else []
    ids_sel   = df_tabla.iloc[filas_sel]["id"].tolist() if filas_sel else []

    if filas_sel:
        if st.button("🗑️ Eliminar pedido(s) seleccionado(s)", type="primary"):
            for id_v in ids_sel:
                eliminar_venta(int(id_v))
            st.success("Pedido(s) eliminado(s).")
            time.sleep(1)
            st.rerun()

    st.divider()

    # --- Editar un pedido ---
    st.subheader("✏️ Editar pedido")
    opciones = [
        f"{int(r['id'])} — #{r['n_pedido']} — {r['cliente'] or 'Sin nombre'} — {r['producto']}"
        for _, r in df_tabla.iterrows()
    ]
    mapa = {opt: int(df_tabla.iloc[i]["id"]) for i, opt in enumerate(opciones)}
    elegido = st.selectbox("Seleccioná un pedido:", ["— Ninguno —"] + opciones, key="inicio_editar_sel")

    if elegido != "— Ninguno —":
        vid   = mapa[elegido]
        venta = df_tabla[df_tabla["id"] == vid].iloc[0]
        pago_actual = venta["medio_pago"] if venta["medio_pago"] in MEDIOS_PAGO else MEDIOS_PAGO[0]

        with st.form("form_editar_venta"):
            col1, col2, col3 = st.columns(3)
            e_cliente  = col1.text_input("Cliente",       value=venta["cliente"] or "")
            e_cantidad = col2.number_input("Cantidad",    min_value=1, value=int(venta["cantidad"]))
            e_precio   = col3.number_input(
                "Precio unit. ($)",
                value=int(round(float(venta["precio_unitario"]))),
                step=100,
                format="%d",
            )

            col4, col5 = st.columns(2)
            e_medio  = col4.selectbox("Forma de pago", MEDIOS_PAGO, index=MEDIOS_PAGO.index(pago_actual))
            e_estado = col5.selectbox(
                "Estado del pedido",
                ESTADOS_PEDIDO,
                index=ESTADOS_PEDIDO.index(venta["estado_display"])
                      if venta["estado_display"] in ESTADOS_PEDIDO else 0,
            )

            if st.form_submit_button("💾 Guardar cambios"):
                cant_orig  = int(venta["cantidad"]) or 1
                costo_orig = (float(venta["total"]) - float(venta["ganancia"])) / cant_orig
                actualizar_venta(vid, e_cliente, e_cantidad, e_precio, e_medio, e_estado, costo_orig)
                diff = e_cantidad - cant_orig
                if diff != 0 and venta["producto"]:
                    prod = obtener_producto_por_nombre(venta["producto"])
                    if prod:
                        if diff > 0:
                            descontar_stock(prod["id"], diff)
                        else:
                            restaurar_stock(prod["id"], abs(diff))
                st.success("Pedido actualizado.")
                time.sleep(1)
                st.rerun()

    st.divider()

    # --- Gestión de entregas (antes pestaña separada) ---
    st.subheader("🚚 Pedidos pendientes de entrega")
    pendientes = df[~df["estado_display"].isin(["✅ Entregado", "❌ Cancelado"])]

    if pendientes.empty:
        st.success("¡Todos los pedidos están entregados! 🎉")
    else:
        st.dataframe(
            pendientes[["n_pedido", "cliente", "producto", "estado_display"]]
            .rename(columns={"estado_display": "estado"}),
            use_container_width=True,
            hide_index=True,
            height=260,
        )
        col_x, col_y, col_z = st.columns([2, 2, 1])
        opciones_p = [
            f"#{r['n_pedido']} — {r['cliente'] or 'Sin nombre'}"
            for _, r in pendientes.iterrows()
        ]
        mapa_p = {
            f"#{r['n_pedido']} — {r['cliente'] or 'Sin nombre'}": int(r["id"])
            for _, r in pendientes.iterrows()
        }
        ped_sel    = col_x.selectbox("Pedido:", opciones_p, key="pend_ped_sel")
        nvo_estado = col_y.selectbox("Nuevo estado:", ESTADOS_PEDIDO, key="pend_estado_sel")
        if col_z.button("Actualizar 🔄"):
            actualizar_estado_pedido(mapa_p[ped_sel], nvo_estado)
            st.success(f"Estado actualizado a {nvo_estado}")
            time.sleep(1)
            st.rerun()
