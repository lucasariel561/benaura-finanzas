"""
🛍️ Nueva Venta — Carrito multi-producto
Permite armar un pedido con varios productos antes de confirmar.
"""

import time
from datetime import date

import pandas as pd
import streamlit as st

from constants import (
    INSUMOS_MATERIALES, INSUMOS_PACKAGING, UNIDAD_INSUMO,
    ESTADOS_PEDIDO, MEDIOS_PAGO,
)
from database import (
    cargar_datos, cargar_productos, cargar_compras_insumos,
    obtener_tarifas_actuales, costo_de,
    insertar_venta, descontar_stock, obtener_proximo_pedido,
)


def _fmt(valor: float) -> str:
    return f"${valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _calcular_costo_materiales(producto_row, tarifas: dict) -> float:
    return (
        float(producto_row["gramos_cera"])      * costo_de(tarifas, "Cera") +
        float(producto_row["gramos_esencia"])   * costo_de(tarifas, "Esencia") +
        float(producto_row["gramos_colorante"]) * costo_de(tarifas, "Colorante") +
        float(producto_row["cm_pabilo"])        * costo_de(tarifas, "Pabilo")
    )


def _calcular_costo_packaging(pack: dict, tarifas: dict) -> float:
    return (
        pack.get("Bolsa", 0)        * costo_de(tarifas, "Bolsa") +
        pack.get("Brochet", 0)      * costo_de(tarifas, "Brochet") +
        pack.get("Sticker", 0)      * costo_de(tarifas, "Sticker") +
        pack.get("Papel Madera", 0) * costo_de(tarifas, "Papel Madera") +
        pack.get("Cinta Bebé", 0)   * costo_de(tarifas, "Cinta Bebé")
    )


def render() -> None:
    st.header("🛍️ Nueva Venta")

    productos_df = cargar_productos()
    if productos_df.empty:
        st.warning("Todavía no cargaste ningún producto. Andá a **Productos** primero.")
        return

    compras_df   = cargar_compras_insumos()
    tarifas      = obtener_tarifas_actuales(compras_df)

    # Avisar si faltan compras de materiales
    faltantes = [i for i in INSUMOS_MATERIALES if i not in tarifas]
    if faltantes:
        st.warning(f"⚠️ Sin precio para: {', '.join(faltantes)}. Registrá una compra en **Productos → Compras**.")

    # Cargar clientes existentes para sugerencia
    df_ventas  = cargar_datos()
    clientes_conocidos = sorted(df_ventas["cliente"].dropna().unique().tolist()) if not df_ventas.empty else []

    # ── Carrito en session_state ──────────────────────────────
    if "carrito" not in st.session_state:
        st.session_state["carrito"] = []

    # ── DATOS DEL PEDIDO (cabecera, fuera del form) ───────────
    st.subheader("📋 Datos del pedido")
    proximo_n = obtener_proximo_pedido()

    col_a, col_b = st.columns(2)
    fecha_pedido = col_a.date_input("Fecha", date.today(), key="nv_fecha")
    col_b.text_input("N° Pedido", value=proximo_n, disabled=True, key="nv_npedido")

    # Autocompletado de cliente
    col_c, col_d = st.columns(2)
    cliente_input = col_c.text_input("Cliente", key="nv_cliente",
                                     placeholder="Nombre del cliente...")
    sugerencias = [c for c in clientes_conocidos if cliente_input.lower() in c.lower()] if cliente_input else []
    if sugerencias and cliente_input not in clientes_conocidos:
        cliente_elegido = col_c.selectbox("¿Es este cliente?", ["(nuevo)"] + sugerencias, key="nv_sug")
        if cliente_elegido != "(nuevo)":
            cliente_final = cliente_elegido
            # Auto-fill teléfono
            tel_auto = df_ventas[df_ventas["cliente"] == cliente_elegido]["telefono"].dropna()
            tel_auto = tel_auto[tel_auto != ""].values
            telefono_val = tel_auto[0] if len(tel_auto) > 0 else ""
        else:
            cliente_final = cliente_input
            telefono_val  = ""
    else:
        cliente_final = cliente_input
        tel_auto = df_ventas[df_ventas["cliente"] == cliente_input]["telefono"].dropna() if cliente_input in clientes_conocidos else pd.Series([])
        tel_auto = tel_auto[tel_auto != ""].values
        telefono_val = tel_auto[0] if len(tel_auto) > 0 else ""

    telefono = col_d.text_input("Teléfono (opcional)", value=telefono_val, key="nv_telefono")

    col_e, col_f = st.columns(2)
    medio_pago = col_e.selectbox("Forma de pago", MEDIOS_PAGO, key="nv_pago")
    estado_ped = col_f.selectbox("Estado del pedido", ESTADOS_PEDIDO, key="nv_estado")

    st.divider()

    # ── AGREGAR PRODUCTO AL CARRITO ───────────────────────────
    st.subheader("➕ Agregar producto")

    col_p1, col_p2 = st.columns([3, 1])
    nombre_prod = col_p1.selectbox("Producto", productos_df["nombre"].tolist(), key="nv_prod")
    prod_sel    = productos_df[productos_df["nombre"] == nombre_prod].iloc[0]

    cantidad_add = col_p2.number_input("Cantidad", min_value=1, value=1, key="nv_cant")

    # Stock warning
    if int(prod_sel["stock"]) < 5:
        st.warning(f"⚠️ Stock bajo: {prod_sel['nombre']} ({int(prod_sel['stock'])} unidades disponibles)")

    # Precio pre-cargado del producto
    precio_add = st.number_input(
        "Precio unitario ($)",
        value=float(prod_sel["precio_unitario"]),
        key="nv_precio",
        help="Podés ajustarlo si querés hacer un descuento puntual."
    )

    # Packaging para esta línea
    st.caption("📦 Packaging para este producto (opcional):")
    pc1, pc2, pc3, pc4, pc5 = st.columns(5)
    pack = {
        "Bolsa":       pc1.number_input("Bolsas",       min_value=0, value=0, key="nv_pk_bolsa"),
        "Brochet":     pc2.number_input("Brochet",      min_value=0, value=0, key="nv_pk_brochet"),
        "Sticker":     pc3.number_input("Stickers",     min_value=0, value=0, key="nv_pk_sticker"),
        "Papel Madera":pc4.number_input("Papel madera", min_value=0, value=0, key="nv_pk_papel"),
        "Cinta Bebé":  pc5.number_input("Cinta bebé",   min_value=0, value=0, key="nv_pk_cinta"),
    }

    costo_mat  = _calcular_costo_materiales(prod_sel, tarifas)
    costo_pack = _calcular_costo_packaging(pack, tarifas)
    costo_unit = costo_mat + costo_pack

    cm1, cm2, cm3 = st.columns(3)
    cm1.metric("Costo materiales",   _fmt(costo_mat))
    cm2.metric("Costo packaging",    _fmt(costo_pack))
    cm3.metric("Costo total/unidad", _fmt(costo_unit))

    if st.button("➕ Agregar al carrito", use_container_width=False):
        st.session_state["carrito"].append({
            "producto":      nombre_prod,
            "producto_id":   int(prod_sel["id"]),
            "cantidad":      cantidad_add,
            "precio_u":      precio_add,
            "costo_u":       costo_unit,
            "packaging":     dict(pack),
        })
        st.rerun()

    st.divider()

    # ── CARRITO ACTUAL ────────────────────────────────────────
    carrito = st.session_state["carrito"]
    if not carrito:
        st.info("El carrito está vacío. Agregá al menos un producto para continuar.")
        return

    st.subheader("🛒 Carrito")

    total_pedido    = 0.0
    ganancia_pedido = 0.0
    for i, item in enumerate(carrito):
        subtotal  = item["cantidad"] * item["precio_u"]
        gan_item  = subtotal - (item["cantidad"] * item["costo_u"])
        total_pedido    += subtotal
        ganancia_pedido += gan_item

        ci1, ci2, ci3, ci4, ci5 = st.columns([3, 1, 1, 1, 1])
        ci1.write(f"**{item['producto']}**")
        ci2.write(f"x{item['cantidad']}")
        ci3.write(_fmt(item["precio_u"]))
        ci4.write(f"costo: {_fmt(item['costo_u'])}")
        if ci5.button("🗑️", key=f"rm_{i}", help="Quitar del carrito"):
            st.session_state["carrito"].pop(i)
            st.rerun()

    st.markdown("---")
    col_t1, col_t2 = st.columns(2)
    col_t1.metric("💰 Total del pedido",   _fmt(total_pedido))
    col_t2.metric("💵 Ganancia estimada",  _fmt(ganancia_pedido))

    col_ok, col_clear = st.columns([2, 1])
    confirmar = col_ok.button("💾 Confirmar pedido", type="primary", use_container_width=True)
    if col_clear.button("🗑️ Vaciar carrito", use_container_width=True):
        st.session_state["carrito"] = []
        st.rerun()

    if confirmar:
        if not cliente_final.strip():
            st.error("Ingresá el nombre del cliente antes de confirmar.")
        else:
            for item in carrito:
                insertar_venta(
                    str(fecha_pedido), proximo_n,
                    cliente_final, telefono,
                    item["producto"], item["cantidad"],
                    item["precio_u"],
                    item["cantidad"] * item["precio_u"],
                    medio_pago, estado_ped,
                    item["cantidad"] * item["precio_u"] - item["cantidad"] * item["costo_u"],
                )
                descontar_stock(item["producto_id"], item["cantidad"])

            st.session_state["carrito"] = []
            st.toast("✅ ¡Pedido guardado!", icon="🎉")
            time.sleep(1)
            st.rerun()
