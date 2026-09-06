"""
🕯️ Productos — Catálogo, compras de insumos y costos actuales
"""

import time
from datetime import date

import pandas as pd
import streamlit as st

from constants import (
    INSUMOS_MATERIALES, INSUMOS_PACKAGING, UNIDAD_INSUMO,
)
from database import (
    cargar_productos, guardar_producto,
    cargar_compras_insumos, insertar_compra_insumo,
    obtener_tarifas_actuales, costo_de,
)


def _fmt(valor: float) -> str:
    return f"${valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def render() -> None:
    st.header("🕯️ Productos")

    tab_catalogo, tab_compras, tab_costos = st.tabs([
        "🕯️ Catálogo", "📦 Compras de insumos", "💲 Costos actuales"
    ])

    productos_df    = cargar_productos()
    compras_df      = cargar_compras_insumos()
    tarifas         = obtener_tarifas_actuales(compras_df)

    # ────────────────────────────────────────────────────────
    # Tab: Catálogo
    # ────────────────────────────────────────────────────────
    with tab_catalogo:
        st.subheader("Catálogo de productos")

        if not productos_df.empty:
            st.dataframe(
                productos_df[["nombre", "stock", "precio_unitario", "margen"]]
                .rename(columns={
                    "nombre": "Producto",
                    "stock": "Stock",
                    "precio_unitario": "Precio ($)",
                    "margen": "Margen",
                })
                .assign(Margen=lambda df: (df["Margen"] * 100).round(1).astype(str) + "%"),
                use_container_width=True,
                hide_index=True,
                height=260,
            )
        else:
            st.info("Todavía no hay productos cargados.")

        st.divider()
        st.subheader("Agregar / editar producto")

        opciones_prod = ["➕ Nuevo producto"] + (
            productos_df["nombre"].tolist() if not productos_df.empty else []
        )
        prod_elegido = st.selectbox(
            "Elegí un producto para editar, o creá uno nuevo:",
            opciones_prod, key="prod_elegido"
        )
        es_nuevo     = prod_elegido == "➕ Nuevo producto"
        prod_actual  = (
            None if es_nuevo
            else productos_df[productos_df["nombre"] == prod_elegido].iloc[0]
        )

        pk = prod_elegido  # key suffix para evitar conflictos

        nombre_p = st.text_input(
            "Nombre del producto",
            value="" if es_nuevo else prod_actual["nombre"],
            key=f"p_nombre_{pk}"
        )
        stock_p = st.number_input(
            "Stock",
            min_value=0,
            value=0 if es_nuevo else int(prod_actual["stock"]),
            key=f"p_stock_{pk}"
        )

        st.caption("Insumos que usa este producto (receta para calcular costo):")
        col_i1, col_i2, col_i3, col_i4 = st.columns(4)
        gr_cera      = col_i1.number_input("Cera (g)",      min_value=0.0, value=0.0 if es_nuevo else float(prod_actual["gramos_cera"]),      key=f"p_cera_{pk}")
        gr_esencia   = col_i2.number_input("Esencia (g)",   min_value=0.0, value=0.0 if es_nuevo else float(prod_actual["gramos_esencia"]),   key=f"p_esencia_{pk}")
        gr_colorante = col_i3.number_input("Colorante (g)", min_value=0.0, value=0.0 if es_nuevo else float(prod_actual["gramos_colorante"]), key=f"p_colorante_{pk}")
        cm_pabilo_p  = col_i4.number_input("Pabilo (cm)",   min_value=0.0, value=0.0 if es_nuevo else float(prod_actual["cm_pabilo"]),        key=f"p_pabilo_{pk}")

        # Costo calculado en tiempo real
        costo_mat = (
            gr_cera      * costo_de(tarifas, "Cera") +
            gr_esencia   * costo_de(tarifas, "Esencia") +
            gr_colorante * costo_de(tarifas, "Colorante") +
            cm_pabilo_p  * costo_de(tarifas, "Pabilo")
        )

        st.divider()

        # Margen POR PRODUCTO (reemplaza el slider global)
        st.caption("Margen de ganancia para este producto:")
        margen_default = 50.0 if es_nuevo else float(prod_actual.get("margen", 0.5)) * 100
        margen_pct = st.number_input(
            "Margen deseado (%)",
            min_value=0.0,
            max_value=99.0,
            value=round(margen_default, 1),
            step=0.5,
            key=f"p_margen_{pk}",
            help="Cuánto porcentaje de ganancia querés sacarle a este producto."
        )
        margen_dec     = margen_pct / 100
        precio_sug     = round(costo_mat / (1 - margen_dec), 2) if margen_dec < 1 else costo_mat

        st.caption(
            f"Costo de materiales: **{_fmt(costo_mat)}** — "
            f"Margen: **{margen_pct:.1f}%** — "
            f"Precio sugerido: **{_fmt(precio_sug)}**"
        )

        precio_key = f"p_precio_{pk}"
        if precio_key not in st.session_state:
            st.session_state[precio_key] = float(prod_actual["precio_unitario"]) if not es_nuevo else precio_sug

        precio_final = st.number_input(
            "Precio unitario ($) — podés ajustarlo manualmente",
            min_value=0.0,
            key=precio_key
        )

        if st.button("💾 Guardar producto", key=f"btn_guardar_{pk}"):
            id_a_guardar = None if es_nuevo else int(prod_actual["id"])
            guardar_producto(
                id_a_guardar, nombre_p, stock_p,
                gr_cera, gr_esencia, gr_colorante, cm_pabilo_p,
                precio_final, margen_dec
            )
            st.success("Producto guardado.")
            time.sleep(1)
            st.rerun()

    # ────────────────────────────────────────────────────────
    # Tab: Compras de insumos
    # ────────────────────────────────────────────────────────
    with tab_compras:
        st.subheader("Registrar compra de insumo")
        st.caption(
            "Cargá lo que compraste y cuánto pagaste en total. "
            "El costo por unidad se calcula solo."
        )

        todos_los_insumos = INSUMOS_MATERIALES + INSUMOS_PACKAGING

        # ⚠️ El selectbox está FUERA del form para que la unidad se actualice
        #    al cambiar de insumo (fix del bug de gramos en Bolsas).
        insumo_elegido = st.selectbox(
            "Insumo",
            todos_los_insumos,
            format_func=lambda x: f"{x}  ({UNIDAD_INSUMO[x]})",
            key="compra_insumo_sel"
        )
        unidad_label = UNIDAD_INSUMO[insumo_elegido]

        with st.form("form_compra_insumo"):
            col_c1, col_c2, col_c3 = st.columns(3)
            fecha_compra    = col_c1.date_input("Fecha de la compra", date.today())
            cantidad_comp   = col_c2.number_input(
                f"Cantidad comprada ({unidad_label})", min_value=0.01, value=1.0
            )
            precio_total_p  = col_c3.number_input("Precio total pagado ($)", min_value=0.0, value=0.0)

            if cantidad_comp > 0 and precio_total_p > 0:
                costo_u = precio_total_p / cantidad_comp
                st.caption(
                    f"➡️ Esto equivale a **{_fmt(costo_u)}** "
                    f"por {unidad_label.rstrip('s') if unidad_label.endswith('s') else unidad_label}"
                )

            if st.form_submit_button("💾 Registrar compra"):
                insertar_compra_insumo(
                    str(fecha_compra), insumo_elegido,
                    cantidad_comp, precio_total_p
                )
                st.success("Compra registrada. El costo de este insumo se actualizó.")
                time.sleep(1)
                st.rerun()

        if not compras_df.empty:
            st.divider()
            st.subheader("Historial de compras")
            st.dataframe(compras_df, use_container_width=True, hide_index=True, height=280)

    # ────────────────────────────────────────────────────────
    # Tab: Costos actuales
    # ────────────────────────────────────────────────────────
    with tab_costos:
        st.subheader("Costos actuales por insumo")
        st.caption("Según la última compra registrada de cada uno.")

        filas = []
        for insumo in INSUMOS_MATERIALES + INSUMOS_PACKAGING:
            info = tarifas.get(insumo)
            if info:
                filas.append({
                    "Insumo": insumo,
                    "Unidad": UNIDAD_INSUMO[insumo],
                    "Costo actual": _fmt(info["costo_unitario"]),
                    "Según compra del": pd.to_datetime(info["fecha"]).strftime("%d/%m/%Y"),
                })
            else:
                filas.append({
                    "Insumo": insumo,
                    "Unidad": UNIDAD_INSUMO[insumo],
                    "Costo actual": "Sin compras",
                    "Según compra del": "—",
                })

        st.dataframe(pd.DataFrame(filas), use_container_width=True, hide_index=True)
