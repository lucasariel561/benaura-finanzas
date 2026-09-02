import streamlit as st
import pandas as pd
from datetime import date
import mysql.connector
from mysql.connector import Error
import urllib.parse
import time

# ==========================================
# 🎨 1. CONFIGURACIÓN VISUAL
# ==========================================
st.set_page_config(page_title="BEN AURA | Panel", page_icon="🕯️", layout="wide")

# Paleta de marca BEN AURA
MARFIL = "#F6F1EA"
CREMA = "#EFE6D8"
ARENA = "#DED0B8"
TAUPE = "#A68F75"
MARRON = "#6F5B47"
OK = "#6F8F6A"
ALERTA = "#C47F4B"
PELIGRO = "#B1554A"

# Nota: en vez de mirar el modo oscuro del sistema operativo (que puede no
# coincidir con el selector de tema propio de Streamlit, arriba a la derecha
# en Settings > Choose app theme), usamos las variables CSS que el propio
# Streamlit ya expone (--background-color, --text-color,
# --secondary-background-color). Esas SIEMPRE reflejan el tema realmente
# activo en la app, sea cual sea el motivo (SO, navegador o el selector
# manual), así que el fondo y los inputs quedan siempre coordinados.
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=Poppins:wght@400;500;600&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Poppins', sans-serif;
    }}

    @keyframes baFadeInUp {{
        from {{ opacity: 0; transform: translateY(10px); }}
        to {{ opacity: 1; transform: translateY(0); }}
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

    /* Encabezado decorativo debajo de cada h1/h2 principal */
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
    [data-testid="stSidebar"] .stRadio > label {{
        font-weight: 600;
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

    /* --- Formularios (contenedor) --- */
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

# ==========================================
# ⚙️ 2. CONEXIÓN A BASE DE DATOS EN LA NUBE (TiDB)
# ==========================================
DB_CONFIG = {
    'host': st.secrets["DB_HOST"],
    'user': st.secrets["DB_USER"],
    'password': st.secrets["DB_PASSWORD"],
    'port': st.secrets["DB_PORT"]
}
DB_NAME = 'benaura_db'

MESES_ES = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio",
    7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
}


def get_connection(use_db=True):
    config = DB_CONFIG.copy()
    if use_db:
        config['database'] = DB_NAME
    return mysql.connector.connect(**config)


def cargar_datos():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM ventas", conn)
    conn.close()
    return df


def insertar_venta(fecha, pedido, cliente, telefono, producto, cantidad, precio_u, total, medio_pago, estado, entrega, ganancia):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO ventas (fecha, n_pedido, cliente, telefono, producto, cantidad, precio_unitario, total, medio_pago, estado, entrega, ganancia)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ''', (fecha, pedido, cliente, telefono, producto, cantidad, precio_u, total, medio_pago, estado, entrega, ganancia))
    conn.commit()
    conn.close()


def actualizar_estado_entrega(id_venta, nuevo_estado):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE ventas SET entrega = %s WHERE id = %s", (nuevo_estado, id_venta))
    conn.commit()
    conn.close()


def eliminar_venta(id_venta):
    """Elimina una venta por su id interno (no por n_pedido, que puede repetirse)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM ventas WHERE id = %s", (id_venta,))
    conn.commit()
    conn.close()


def obtener_proximo_pedido():
    # Se usa el MAXIMO numero de pedido existente (no un COUNT) para que
    # borrar pedidos de prueba no genere numeros de pedido repetidos despues.
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COALESCE(MAX(CAST(n_pedido AS UNSIGNED)), 0) FROM ventas")
    max_pedido = cursor.fetchone()[0]
    conn.close()
    return f"{(int(max_pedido) + 1):03d}"


def actualizar_venta(id_venta, cliente, cantidad, precio_unitario, medio_pago, estado, entrega, costo_unitario_original):
    """Recalcula total y ganancia usando el costo unitario que ya tenia la
    venta (derivado de total y ganancia guardados), para no perder ese dato
    aunque la tabla ventas no tenga una columna de costo unitario propia."""
    total_nuevo = cantidad * precio_unitario
    ganancia_nueva = total_nuevo - (cantidad * costo_unitario_original)
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE ventas SET cliente=%s, cantidad=%s, precio_unitario=%s, total=%s,
        ganancia=%s, medio_pago=%s, estado=%s, entrega=%s WHERE id=%s
    ''', (cliente, cantidad, precio_unitario, total_nuevo, ganancia_nueva, medio_pago, estado, entrega, id_venta))
    conn.commit()
    conn.close()


# ==========================================
# 🕯️ FUNCIONES: PRODUCTOS Y TARIFAS DE INSUMOS
# ==========================================

def cargar_productos():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM productos ORDER BY nombre", conn)
    conn.close()
    return df


def guardar_producto(id_producto, nombre, stock, gramos_cera, gramos_esencia, gramos_colorante, cm_pabilo, precio_unitario):
    conn = get_connection()
    cursor = conn.cursor()
    if id_producto:
        cursor.execute('''
            UPDATE productos SET nombre=%s, stock=%s, gramos_cera=%s, gramos_esencia=%s,
            gramos_colorante=%s, cm_pabilo=%s, precio_unitario=%s WHERE id=%s
        ''', (nombre, stock, gramos_cera, gramos_esencia, gramos_colorante, cm_pabilo, precio_unitario, id_producto))
    else:
        cursor.execute('''
            INSERT INTO productos (nombre, stock, gramos_cera, gramos_esencia, gramos_colorante, cm_pabilo, precio_unitario)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        ''', (nombre, stock, gramos_cera, gramos_esencia, gramos_colorante, cm_pabilo, precio_unitario))
    conn.commit()
    conn.close()


def descontar_stock(id_producto, cantidad):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE productos SET stock = GREATEST(stock - %s, 0) WHERE id = %s", (cantidad, id_producto))
    conn.commit()
    conn.close()


def restaurar_stock(id_producto, cantidad):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE productos SET stock = stock + %s WHERE id = %s", (cantidad, id_producto))
    conn.commit()
    conn.close()


def obtener_producto_por_nombre(nombre_producto):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id FROM productos WHERE nombre = %s", (nombre_producto,))
    fila = cursor.fetchone()
    conn.close()
    return fila


def eliminar_venta(id_venta):
    """Elimina una venta y restaura el stock del producto."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT producto, cantidad FROM ventas WHERE id = %s", (id_venta,))
    venta = cursor.fetchone()
    if venta and venta['producto']:
        prod = obtener_producto_por_nombre(venta['producto'])
        if prod:
            restaurar_stock(prod['id'], venta['cantidad'])
    cursor.execute("DELETE FROM ventas WHERE id = %s", (id_venta,))
    conn.commit()
    conn.close()


def obtener_config_insumos():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM config_insumos WHERE id = 1")
    fila = cursor.fetchone()
    conn.close()
    return fila


def guardar_margen(margen):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE config_insumos SET margen_objetivo=%s WHERE id=1", (margen,))
    conn.commit()
    conn.close()


# ==========================================
# 🧾 FUNCIONES: COMPRAS DE INSUMOS (precio real, no una tarifa fija)
# ==========================================

UNIDAD_INSUMO = {
    "Cera": "gramos", "Esencia": "gramos", "Colorante": "gramos", "Pabilo": "cm",
    "Bolsa": "unidad", "Brochet": "unidad", "Sticker": "unidad",
    "Papel Madera": "unidad", "Cinta Bebé": "unidad",
}
INSUMOS_MATERIALES = ["Cera", "Esencia", "Colorante", "Pabilo"]
INSUMOS_PACKAGING = ["Bolsa", "Brochet", "Sticker", "Papel Madera", "Cinta Bebé"]


def cargar_compras_insumos():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM compras_insumos ORDER BY fecha DESC, id DESC", conn)
    conn.close()
    return df


def insertar_compra_insumo(fecha, insumo, cantidad, precio_total):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO compras_insumos (fecha, insumo, cantidad, precio_total)
        VALUES (%s, %s, %s, %s)
    ''', (fecha, insumo, cantidad, precio_total))
    conn.commit()
    conn.close()


def obtener_tarifas_actuales(compras_df):
    """Para cada insumo, calcula el costo por unidad segun la COMPRA MAS
    RECIENTE registrada (no un promedio historico), asi el numero siempre
    refleja lo ultimo que se pago realmente."""
    tarifas = {}
    if not compras_df.empty:
        ultima_por_insumo = compras_df.sort_values(['fecha', 'id']).groupby('insumo').tail(1)
        for _, fila in ultima_por_insumo.iterrows():
            cantidad = float(fila['cantidad'])
            tarifas[fila['insumo']] = {
                'costo_unitario': (float(fila['precio_total']) / cantidad) if cantidad else 0.0,
                'fecha': fila['fecha'],
            }
    return tarifas


def costo_de(tarifas, insumo):
    return tarifas.get(insumo, {}).get('costo_unitario', 0.0)


# Cargamos todos los datos al abrir la app
df = cargar_datos()
productos_df = cargar_productos()
config_insumos = obtener_config_insumos()
compras_insumos_df = cargar_compras_insumos()
tarifas_actuales = obtener_tarifas_actuales(compras_insumos_df)

# ==========================================
# 🗂️ 4. MENÚ LATERAL DE NAVEGACIÓN
# ==========================================
with st.sidebar:
    st.title("🕯️ BEN AURA")
    st.markdown("*Aromas que abrazan.*")
    st.divider()
    menu = st.radio("Navegación", [
        "📊 Dashboard General",
        "📈 Estadísticas por Mes",
        "🕯️ Producto",
        "🛍️ Cargar Venta",
        "🚚 Gestión de Pedidos",
        "📲 CRM y Promociones",
        "📢 Anuncios (Próximamente)"
    ], label_visibility="collapsed")

# ==========================================
# 📊 SECCIÓN: DASHBOARD GENERAL
# ==========================================
if menu == "📊 Dashboard General":
    st.header("📊 Rendimiento Diario")
    if not df.empty:
        df['fecha'] = pd.to_datetime(df['fecha'])
        df['periodo'] = df['fecha'].dt.to_period('M')
        df['mes_anio'] = df['periodo'].apply(lambda p: f"{MESES_ES[p.month]} {p.year}")

        periodos_ordenados = sorted(df['periodo'].unique())
        meses_disponibles = [f"{MESES_ES[p.month]} {p.year}" for p in periodos_ordenados]

        mes_seleccionado = st.selectbox("📅 Filtrar movimientos por mes:", meses_disponibles, index=len(meses_disponibles) - 1)

        df_mes = df[df['mes_anio'] == mes_seleccionado]
        ventas_mes = float(df_mes['total'].sum())
        ganancia_mes = float(df_mes['ganancia'].sum())
        ganancia_historica = float(df['ganancia'].sum())

        st.markdown(f"### 📈 Resumen de {mes_seleccionado}")
        col1, col2, col3 = st.columns(3)
        col1.metric("💰 Ventas del Mes", f"${ventas_mes:,.2f}")
        col2.metric("📦 Pedidos del Mes", len(df_mes))
        col3.metric("💵 Ganancia del Mes", f"${ganancia_mes:,.2f}")

        st.divider()
        st.metric("💎 Ganancia Histórica Total", f"${ganancia_historica:,.2f}")

        tabla_a_mostrar = df_mes.drop(columns=['periodo', 'mes_anio'])
        columnas_tabla = ['n_pedido', 'fecha', 'cliente', 'producto', 'cantidad', 'precio_unitario', 'total', 'estado', 'entrega']
        st.subheader("Tabla de pedidos del mes")
        st.caption("Seleccioná filas con el checkbox de la izquierda para eliminar.")
        evento = st.dataframe(
            tabla_a_mostrar[columnas_tabla],
            use_container_width=True,
            hide_index=True,
            height=360,
            on_select="rerun",
            selection_mode="multi-row",
            key="tabla_ventas_dashboard"
        )

        filas_sel = evento.selection.rows if evento and evento.selection else []
        ids_sel = tabla_a_mostrar.iloc[filas_sel]['id'].tolist() if filas_sel else []

        if filas_sel:
            col_del, col_esp = st.columns([1, 3])
            with col_del:
                if st.button("🗑️ Eliminar pedido(s) seleccionado(s)", type="primary"):
                    for id_venta in ids_sel:
                        eliminar_venta(id_venta)
                    st.success("Pedido(s) eliminado(s).")
                    time.sleep(1)
                    st.rerun()

        st.divider()
        st.subheader("✏️ Editar un pedido")
        opciones_venta = [
            f"{int(fila['id'])} — #{fila['n_pedido']} — {fila['cliente'] or 'Sin cliente'} — {fila['producto']}"
            for _, fila in tabla_a_mostrar.iterrows()
        ]
        mapa_ventas = {
            opt: int(tabla_a_mostrar.iloc[i]['id'])
            for i, opt in enumerate(opciones_venta)
        }
        venta_elegida_label = st.selectbox("Seleccioná un pedido para editar:", ["— Ninguno —"] + opciones_venta, key="editar_venta_select")

        if venta_elegida_label != "— Ninguno —":
            venta_id = mapa_ventas[venta_elegida_label]
            venta_sel = tabla_a_mostrar[tabla_a_mostrar['id'] == venta_id].iloc[0]

            opciones_pago = ["Transferencia", "Efectivo"]
            opciones_estado = ["Pendiente", "Pagado", "Cancelado"]
            opciones_entrega = ["Retira", "Envío", "Entregado"]

            with st.form("form_editar_venta"):
                col_e1, col_e2, col_e3 = st.columns(3)
                e_cliente = col_e1.text_input("Cliente", value=venta_sel['cliente'] or "")
                e_cantidad = col_e2.number_input("Cantidad", min_value=1, value=int(venta_sel['cantidad']))
                e_precio = col_e3.number_input("Precio unit. ($)", value=float(venta_sel['precio_unitario']))

                col_e4, col_e5, col_e6 = st.columns(3)
                pago_actual = venta_sel['medio_pago'] if venta_sel['medio_pago'] in opciones_pago else opciones_pago[0]
                e_medio = col_e4.selectbox("Pago", opciones_pago, index=opciones_pago.index(pago_actual))
                e_estado = col_e5.selectbox("Estado", opciones_estado, index=opciones_estado.index(venta_sel['estado']))
                e_entrega = col_e6.selectbox("Entrega", opciones_entrega, index=opciones_entrega.index(venta_sel['entrega']))

                guardar_edicion = st.form_submit_button("💾 Guardar cambios")

                if guardar_edicion:
                    cantidad_original = venta_sel['cantidad'] or 1
                    costo_unitario_original = (float(venta_sel['total']) - float(venta_sel['ganancia'])) / cantidad_original
                    actualizar_venta(int(venta_sel['id']), e_cliente, e_cantidad, e_precio, e_medio, e_estado, e_entrega, costo_unitario_original)
                    diferencia = e_cantidad - int(cantidad_original)
                    if diferencia != 0 and venta_sel['producto']:
                        prod = obtener_producto_por_nombre(venta_sel['producto'])
                        if prod:
                            if diferencia > 0:
                                descontar_stock(prod['id'], diferencia)
                            else:
                                restaurar_stock(prod['id'], abs(diferencia))
                    st.success("Pedido actualizado.")
                    time.sleep(1)
                    st.rerun()
    else:
        st.info("Aún no hay ventas registradas.")

# ==========================================
# 📈 SECCIÓN: ESTADÍSTICAS POR MES
# ==========================================
elif menu == "📈 Estadísticas por Mes":
    st.header("📈 Evolución del Negocio")
    st.write("Analizá cómo crecen las ventas y ganancias de BEN AURA mes a mes.")

    if not df.empty:
        df['fecha'] = pd.to_datetime(df['fecha'])
        df['periodo'] = df['fecha'].dt.to_period('M')
        df['Mes'] = df['periodo'].apply(lambda p: f"{MESES_ES[p.month]} {p.year}")
        orden_periodos = df.sort_values('periodo')['Mes'].unique().tolist()

        df_agrupado = df.groupby('Mes').agg(
            Ingresos_Totales=('total', 'sum'),
            Ganancia_Neta=('ganancia', 'sum'),
            Unidades_Vendidas=('cantidad', 'sum'),
            Total_Pedidos=('n_pedido', 'count')
        ).reindex(orden_periodos).reset_index()

        st.subheader("Resumen Numérico Detallado")
        st.dataframe(df_agrupado, use_container_width=True, hide_index=True, height=420)

        st.divider()
        st.subheader("Curva de Ganancias Netas")
        st.bar_chart(data=df_agrupado, x='Mes', y='Ganancia_Neta', color=MARRON)
    else:
        st.info("Aún no hay ventas suficientes para armar las estadísticas mensuales.")

# ==========================================
# 🕯️ SECCIÓN: PRODUCTO
# ==========================================
elif menu == "🕯️ Producto":
    st.header("🕯️ Productos")

    tab_compras, tab_costos, tab_catalogo = st.tabs(["📦 Compras de Insumos", "💲 Costos y Margen", "🕯️ Catálogo"])

    with tab_compras:
        st.subheader("Registrar compra de insumo")
        st.caption("Cargá lo que compraste de verdad (lo que pagaste y cuánto). El costo por unidad se calcula solo.")
        with st.form("form_compra_insumo"):
            col_c1, col_c2 = st.columns(2)
            todos_los_insumos = INSUMOS_MATERIALES + INSUMOS_PACKAGING
            insumo_elegido = col_c1.selectbox(
                "Insumo",
                todos_los_insumos,
                format_func=lambda x: f"{x} ({UNIDAD_INSUMO[x]})"
            )
            fecha_compra = col_c2.date_input("Fecha de la compra", date.today())

            col_c3, col_c4 = st.columns(2)
            cantidad_comprada = col_c3.number_input(f"Cantidad comprada ({UNIDAD_INSUMO[insumo_elegido]})", min_value=0.01, value=1.0)
            precio_total_pagado = col_c4.number_input("Precio total pagado ($)", min_value=0.0, value=0.0)

            if cantidad_comprada > 0:
                st.caption(f"➡️ Esto da ${precio_total_pagado / cantidad_comprada:,.2f} por {UNIDAD_INSUMO[insumo_elegido][:-1] if UNIDAD_INSUMO[insumo_elegido].endswith('s') else UNIDAD_INSUMO[insumo_elegido]}")

            guardar_compra = st.form_submit_button("💾 Registrar compra")
            if guardar_compra:
                insertar_compra_insumo(str(fecha_compra), insumo_elegido, cantidad_comprada, precio_total_pagado)
                st.success("Compra registrada. El costo de este insumo ya se actualizó.")
                time.sleep(1)
                st.rerun()

    with tab_costos:
        st.subheader("Costos actuales por insumo")
        st.caption("Según tu última compra de cada uno.")
        filas_costos = []
        for insumo in INSUMOS_MATERIALES + INSUMOS_PACKAGING:
            info = tarifas_actuales.get(insumo)
            if info:
                filas_costos.append({
                    "Insumo": insumo,
                    "Costo actual": f"${info['costo_unitario']:,.2f} / {UNIDAD_INSUMO[insumo]}",
                    "Según compra del": pd.to_datetime(info['fecha']).strftime('%d/%m/%Y')
                })
            else:
                filas_costos.append({"Insumo": insumo, "Costo actual": "Sin compras registradas", "Según compra del": "—"})
        st.dataframe(pd.DataFrame(filas_costos), use_container_width=True, hide_index=True)

        st.divider()
        st.subheader("Margen objetivo para sugerir precios")
        margen = st.slider("Margen objetivo", 0.0, 0.9, float(config_insumos['margen_objetivo']), step=0.05, key="tarifa_margen")
        if st.button("Guardar margen"):
            guardar_margen(margen)
            st.success("Margen actualizado.")
            time.sleep(1)
            st.rerun()

    with tab_catalogo:
        st.subheader("Catálogo de productos")

        if not productos_df.empty:
            st.dataframe(
                productos_df[['nombre', 'stock', 'precio_unitario']],
                use_container_width=True, hide_index=True, height=280
            )
        else:
            st.info("Todavía no hay productos cargados.")

        st.divider()
        st.subheader("Agregar / editar producto")

        opciones_prod = ["➕ Nuevo producto"] + (productos_df['nombre'].tolist() if not productos_df.empty else [])
        prod_elegido = st.selectbox("Elegí un producto para editar, o creá uno nuevo:", opciones_prod, key="prod_elegido")
        prod_actual = None if prod_elegido == "➕ Nuevo producto" else productos_df[productos_df['nombre'] == prod_elegido].iloc[0]

        nombre_p = st.text_input("Nombre del producto", value=prod_actual['nombre'] if prod_actual is not None else "", key=f"p_nombre_{prod_elegido}")
        stock_p = st.number_input("Stock", min_value=0, value=int(prod_actual['stock']) if prod_actual is not None else 0, key=f"p_stock_{prod_elegido}")

        st.caption("Insumos que usa este producto (para calcular su costo):")
        col_i1, col_i2, col_i3, col_i4 = st.columns(4)
        gr_cera = col_i1.number_input("Cera (gramos)", min_value=0.0, value=float(prod_actual['gramos_cera']) if prod_actual is not None else 0.0, key=f"p_cera_{prod_elegido}")
        gr_esencia = col_i2.number_input("Esencia (gramos)", min_value=0.0, value=float(prod_actual['gramos_esencia']) if prod_actual is not None else 0.0, key=f"p_esencia_{prod_elegido}")
        gr_colorante = col_i3.number_input("Colorante (gramos)", min_value=0.0, value=float(prod_actual['gramos_colorante']) if prod_actual is not None else 0.0, key=f"p_colorante_{prod_elegido}")
        cm_pabilo_p = col_i4.number_input("Pabilo (cm)", min_value=0.0, value=float(prod_actual['cm_pabilo']) if prod_actual is not None else 0.0, key=f"p_pabilo_{prod_elegido}")

        costo_mat_preview = (
            gr_cera * costo_de(tarifas_actuales, "Cera") +
            gr_esencia * costo_de(tarifas_actuales, "Esencia") +
            gr_colorante * costo_de(tarifas_actuales, "Colorante") +
            cm_pabilo_p * costo_de(tarifas_actuales, "Pabilo")
        )
        margen_actual = float(config_insumos['margen_objetivo'])
        precio_sugerido = round(costo_mat_preview / (1 - margen_actual), 2) if margen_actual < 1 else round(costo_mat_preview, 2)

        precio_key = f"p_precio_{prod_elegido}"
        if precio_key not in st.session_state:
            st.session_state[precio_key] = float(prod_actual['precio_unitario']) if prod_actual is not None else 0.0

        st.caption(f"Costo materiales: ${costo_mat_preview:,.2f} — Margen: {int(margen_actual*100)}% — Precio sugerido: ${precio_sugerido:,.2f}")
        precio_final = st.number_input("Precio unitario ($) — escribí el precio o usá el sugerido", min_value=0.0, key=precio_key)

        if st.button("💾 Guardar producto"):
            id_a_guardar = int(prod_actual['id']) if prod_actual is not None else None
            guardar_producto(id_a_guardar, nombre_p, stock_p, gr_cera, gr_esencia, gr_colorante, cm_pabilo_p, precio_final)
            st.success("Producto guardado.")
            time.sleep(1)
            st.rerun()

# ==========================================
# 🛍️ SECCIÓN: CARGAR VENTA
# ==========================================
elif menu == "🛍️ Cargar Venta":
    st.header("🛍️ Registrar Nuevo Pedido")
    if 'venta_exitosa' in st.session_state and st.session_state.venta_exitosa:
        st.toast('✅ ¡Venta guardada en la base de datos!', icon='🎉')
        st.session_state.venta_exitosa = False

    if productos_df.empty:
        st.warning("Todavía no cargaste ningún producto. Andá a la pestaña 'Producto' primero.")
    else:
        proximo_n_pedido = obtener_proximo_pedido()

        insumos_faltantes = [i for i in INSUMOS_MATERIALES if i not in tarifas_actuales]
        if insumos_faltantes:
            st.warning(f"⚠️ Faltan compras de: {', '.join(insumos_faltantes)}. Andá a 'Producto' y cargá al menos una compra de cada insumo para calcular costos reales.")

        nombre_producto = st.selectbox("Producto", productos_df['nombre'].tolist(), key="venta_producto")
        producto_sel = productos_df[productos_df['nombre'] == nombre_producto].iloc[0]

        if int(producto_sel['stock']) < 5:
            st.warning(f"⚠️ Stock bajo: {producto_sel['nombre']} ({int(producto_sel['stock'])} unidades)")

        costo_materiales = (
            float(producto_sel['gramos_cera']) * costo_de(tarifas_actuales, "Cera") +
            float(producto_sel['gramos_esencia']) * costo_de(tarifas_actuales, "Esencia") +
            float(producto_sel['gramos_colorante']) * costo_de(tarifas_actuales, "Colorante") +
            float(producto_sel['cm_pabilo']) * costo_de(tarifas_actuales, "Pabilo")
        )

        st.subheader("🎁 Packaging para esta venta")
        col_p1, col_p2, col_p3, col_p4, col_p5 = st.columns(5)
        n_bolsas = col_p1.number_input("Bolsas", min_value=0, value=0, key="pk_bolsas")
        n_brochet = col_p2.number_input("Brochet", min_value=0, value=0, key="pk_brochet")
        n_sticker = col_p3.number_input("Sticker", min_value=0, value=0, key="pk_sticker")
        n_papel = col_p4.number_input("Papel madera", min_value=0, value=0, key="pk_papel")
        n_cinta = col_p5.number_input("Cinta bebé", min_value=0, value=0, key="pk_cinta")

        costo_pack = (
            n_bolsas * costo_de(tarifas_actuales, "Bolsa") +
            n_brochet * costo_de(tarifas_actuales, "Brochet") +
            n_sticker * costo_de(tarifas_actuales, "Sticker") +
            n_papel * costo_de(tarifas_actuales, "Papel Madera") +
            n_cinta * costo_de(tarifas_actuales, "Cinta Bebé")
        )

        costo_sugerido = costo_materiales + costo_pack

        st.divider()
        st.subheader("📋 Resumen de costos")
        col_r1, col_r2, col_r3 = st.columns(3)
        col_r1.metric("📦 Materiales", f"${costo_materiales:,.2f}")
        col_r2.metric("🎁 Packaging", f"${costo_pack:,.2f}")
        col_r3.metric("💲 Costo total/unit", f"${costo_sugerido:,.2f}")

        if st.session_state.get('venta_precio_u') is None:
            st.session_state['venta_precio_u'] = float(producto_sel['precio_unitario'])

        with st.form("form_nueva_venta"):
            col_a, col_b, col_c = st.columns(3)
            fecha = col_a.date_input("Fecha", date.today())
            pedido = col_b.text_input("N° Pedido", value=proximo_n_pedido, disabled=True)
            cliente = col_c.text_input("Nombre del Cliente")

            telefono = st.text_input("Teléfono del Cliente (Opcional - Ej: 54911...)")

            col_d, col_e, col_f = st.columns(3)
            cantidad = col_d.number_input("Cantidad", min_value=1, value=1)
            precio_u = col_e.number_input("Precio unit. ($)", value=float(producto_sel['precio_unitario']))
            costo_u = col_f.number_input("Costo unit. ($)", value=float(costo_sugerido))

            col_g, col_h, col_i = st.columns(3)
            medio_pago = col_g.selectbox("Pago", ["Transferencia", "Efectivo"])
            estado = col_h.selectbox("Estado", ["Pendiente", "Pagado", "Cancelado"])
            entrega = col_i.selectbox("Entrega", ["Retira", "Envío", "Entregado"])

            total_preview = cantidad * precio_u
            ganancia_preview = total_preview - (cantidad * costo_u)
            col_gp1, col_gp2 = st.columns(2)
            col_gp1.metric("💰 Total", f"${total_preview:,.2f}")
            col_gp2.metric("💵 Ganancia estimada", f"${ganancia_preview:,.2f}")

            submit = st.form_submit_button("Guardar Venta 💾")

            if submit:
                insertar_venta(str(fecha), proximo_n_pedido, cliente, telefono, nombre_producto, cantidad, precio_u, total_preview, medio_pago, estado, entrega, ganancia_preview)
                descontar_stock(int(producto_sel['id']), cantidad)
                st.session_state.venta_exitosa = True
                st.rerun()

# ==========================================
# 🚚 SECCIÓN: GESTIÓN DE PEDIDOS
# ==========================================
elif menu == "🚚 Gestión de Pedidos":
    st.header("🚚 Seguimiento de Envíos y Entregas")

    if not df.empty:
        pendientes = df[df['entrega'] != 'Entregado']
        if not pendientes.empty:
            st.dataframe(pendientes[['n_pedido', 'cliente', 'producto', 'entrega', 'estado']], use_container_width=True, hide_index=True, height=420)
            st.divider()
            with st.form("form_actualizar_entrega"):
                col_x, col_y = st.columns(2)
                opciones_pedido = [f"{fila['n_pedido']} — {fila['cliente']}" for _, fila in pendientes.iterrows()]
                mapa_ids = {f"{fila['n_pedido']} — {fila['cliente']}": int(fila['id']) for _, fila in pendientes.iterrows()}
                pedido_seleccionado = col_x.selectbox("Seleccionar pedido:", opciones_pedido)
                nuevo_estado = col_y.selectbox("Cambiar estado a:", ["Entregado", "Envío", "Retira"])
                btn_actualizar = st.form_submit_button("Actualizar 🔄")

                if btn_actualizar:
                    id_venta = mapa_ids[pedido_seleccionado]
                    actualizar_estado_entrega(id_venta, nuevo_estado)
                    st.success(f"¡Pedido actualizado a {nuevo_estado}!")
                    time.sleep(1)
                    st.rerun()
        else:
            st.success("¡Excelente! Todos los pedidos están entregados. 🎉")
    else:
        st.info("Aún no hay pedidos para gestionar.")

# ==========================================
# 📲 SECCIÓN: CRM Y PROMOCIONES
# ==========================================
elif menu == "📲 CRM y Promociones":
    st.header("📲 Fidelización de Clientes")
    if not df.empty:
        clientes_con_telefono = df[df['telefono'].fillna('') != '']
        if not clientes_con_telefono.empty:
            cliente_elegido = st.selectbox("1. Seleccioná un cliente:", clientes_con_telefono['cliente'].unique())
            tel_cliente = clientes_con_telefono[clientes_con_telefono['cliente'] == cliente_elegido]['telefono'].iloc[0]

            st.markdown("### 2. Armá tu oferta del momento:")
            default_msg = f"¡Hola {cliente_elegido}! Te compartimos las novedades de BEN AURA. ¡Te esperamos!"
            if 'crm_mensaje_default' not in st.session_state:
                st.session_state['crm_mensaje_default'] = default_msg
            mensaje_personalizado = st.text_area(
                "Podés modificar este texto:",
                value=st.session_state.get('crm_mensaje_template', default_msg),
                height=120,
                key="crm_text_area"
            )

            if st.button("💾 Guardar plantilla"):
                st.session_state['crm_mensaje_template'] = mensaje_personalizado
                st.success("Plantilla guardada para esta sesión.")

            link_wsp = f"https://wa.me/{tel_cliente}?text={urllib.parse.quote(mensaje_personalizado)}"
            st.markdown(f'<br><a href="{link_wsp}" target="_blank"><button style="background-color:#25D366; color:white; padding:10px 20px; border:none; border-radius:5px; font-weight:bold; cursor:pointer;">Enviar por WhatsApp Business 🚀</button></a>', unsafe_allow_html=True)
        else:
            st.warning("Aún no tenés clientes con teléfono registrado.")
    else:
        st.info("Aún no hay clientes registrados.")

# ==========================================
# 📢 SECCIÓN: ANUNCIOS
# ==========================================
elif menu == "📢 Anuncios (Próximamente)":
    st.header("📢 Seguimiento de Pauta Publicitaria")
    st.info("Esta sección está en construcción para conectar las métricas de tus anuncios.")