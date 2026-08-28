import streamlit as st
import pandas as pd
from datetime import date
import mysql.connector
from mysql.connector import Error
import urllib.parse
import time

st.set_page_config(page_title="BEN AURA | Panel", page_icon="🕯️", layout="wide")


MARFIL = "#F6F1EA"
CREMA = "#EFE6D8"
ARENA = "#DED0B8"
TAUPE = "#A68F75"
MARRON = "#6F5B47"
OK = "#6F8F6A"
ALERTA = "#C47F4B"
PELIGRO = "#B1554A"


st.markdown(f"""
    <style>
    .stApp {{ background-color: {MARFIL}; }}

    h1, h2, h3 {{ color: {MARRON}; font-family: 'Georgia', serif; }}

    [data-testid="stSidebar"] {{
        background-color: {MARRON};
    }}
    [data-testid="stSidebar"] * {{
        color: {MARFIL} !important;
    }}
    [data-testid="stSidebar"] .stRadio > label {{
        font-weight: 600;
    }}
    [data-testid="stSidebar"] [role="radiogroup"] label {{
        background-color: rgba(255,255,255,0.06);
        border-radius: 8px;
        padding: 8px 10px;
        margin-bottom: 4px;
    }}
    [data-testid="stSidebar"] [role="radiogroup"] label:hover {{
        background-color: rgba(255,255,255,0.14);
    }}

    [data-testid="stMetric"] {{
        background-color: white;
        border: 1px solid {ARENA};
        border-radius: 10px;
        padding: 14px 16px;
    }}
    [data-testid="stMetricLabel"] {{ color: {TAUPE}; }}
    [data-testid="stMetricValue"] {{ color: {MARRON}; }}

    div.stButton > button, .stFormSubmitButton > button {{
        background-color: {MARRON};
        color: white;
        border: none;
        border-radius: 6px;
    }}
    div.stButton > button:hover, .stFormSubmitButton > button:hover {{
        background-color: {TAUPE};
        color: white;
    }}

    [data-testid="stDataFrame"] {{
        border: 1px solid {ARENA};
        border-radius: 8px;
    }}

    div[data-baseweb="select"] > div {{
        min-height: 42px;
    }}
    ul[data-testid="stSelectboxVirtualDropdown"] li {{
        white-space: normal;
    }}
    </style>
""", unsafe_allow_html=True)

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


def actualizar_estado_entrega(pedido, nuevo_estado):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE ventas SET entrega = %s WHERE n_pedido = %s", (nuevo_estado, pedido))
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


df = cargar_datos()

CATALOGO = {
    "Margarita Individual": {"costo": 800.0, "precio": 2800.0},
    "Margarita en Tarjeta": {"costo": 850.0, "precio": 3000.0},
    "Ramo Premium (5 Flores)": {"costo": 4000.0, "precio": 12000.0},
    "Set Mini Bubbles (Pack x3)": {"costo": 2400.0, "precio": 6500.0},
    "Vela Bubble Grande": {"costo": 3000.0, "precio": 8000.0},
    "Wax Melts: Mini Margaritas (x6)": {"costo": 1000.0, "precio": 3500.0},
    "Combo Detalles (3 Marg. en Tarjeta)": {"costo": 2550.0, "precio": 8000.0},
    "Combo Aromas (1 Bubble + 1 Ramo)": {"costo": 7000.0, "precio": 18500.0},
    "Otro": {"costo": 0.0, "precio": 0.0}
}

with st.sidebar:
    st.title("🕯️ BEN AURA")
    st.markdown("*Aromas que abrazan.*")
    st.divider()
    menu = st.radio("Navegación", [
        "📊 Dashboard General",
        "📈 Estadísticas por Mes",
        "🛍️ Cargar Venta",
        "🚚 Gestión de Pedidos",
        "📲 CRM y Promociones",
        "📢 Anuncios (Próximamente)"
    ], label_visibility="collapsed")

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

        st.caption("Hacé click a la izquierda de una fila para seleccionarla y poder eliminarla.")
        tabla_a_mostrar = df_mes.drop(columns=['periodo', 'mes_anio'])
        evento = st.dataframe(
            tabla_a_mostrar,
            use_container_width=True,
            hide_index=True,
            height=420,
            on_select="rerun",
            selection_mode="multi-row",
            key="tabla_ventas_dashboard"
        )

        filas_sel = evento.selection.rows if evento and evento.selection else []
        if filas_sel:
            ids_sel = tabla_a_mostrar.iloc[filas_sel]['id'].tolist()
            st.warning(f"Seleccionaste {len(ids_sel)} pedido(s) para eliminar. Esta acción no se puede deshacer.")
            if st.button("🗑️ Eliminar pedido(s) seleccionado(s)"):
                for id_venta in ids_sel:
                    eliminar_venta(id_venta)
                st.success("Pedido(s) eliminado(s).")
                time.sleep(1)
                st.rerun()
    else:
        st.info("Aún no hay ventas registradas.")

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

elif menu == "🛍️ Cargar Venta":
    st.header("🛍️ Registrar Nuevo Pedido")
    if 'venta_exitosa' in st.session_state and st.session_state.venta_exitosa:
        st.toast('✅ ¡Venta guardada en la base de datos!', icon='🎉')
        st.session_state.venta_exitosa = False

    proximo_n_pedido = obtener_proximo_pedido()

    with st.form("form_nueva_venta"):
        col_a, col_b, col_c = st.columns(3)
        fecha = col_a.date_input("Fecha", date.today())
        pedido = col_b.text_input("N° Pedido", value=proximo_n_pedido, disabled=True)
        cliente = col_c.text_input("Nombre del Cliente")

        telefono = st.text_input("Teléfono del Cliente (Opcional - Ej: 54911...)")
        producto_seleccionado = st.selectbox("Producto", list(CATALOGO.keys()))

        col_d, col_e, col_f = st.columns(3)
        cantidad = col_d.number_input("Cantidad", min_value=1, value=1)
        precio_u = col_e.number_input("Precio unit. ($)", value=CATALOGO[producto_seleccionado]["precio"])
        costo_u = col_f.number_input("Costo unit. ($)", value=CATALOGO[producto_seleccionado]["costo"])

        col_g, col_h, col_i = st.columns(3)
        medio_pago = col_g.selectbox("Pago", ["Transferencia", "Efectivo", "Mercado Pago"])
        estado = col_h.selectbox("Estado", ["Pendiente", "Pagado", "Cancelado"])
        entrega = col_i.selectbox("Entrega", ["Retira", "Envío", "Entregado"])

        submit = st.form_submit_button("Guardar Venta 💾")

        if submit:
            total_calc = cantidad * precio_u
            ganancia_calc = total_calc - (cantidad * costo_u)
            insertar_venta(str(fecha), proximo_n_pedido, cliente, telefono, producto_seleccionado, cantidad, precio_u, total_calc, medio_pago, estado, entrega, ganancia_calc)
            st.session_state.venta_exitosa = True
            st.rerun()


elif menu == "🚚 Gestión de Pedidos":
    st.header("🚚 Seguimiento de Envíos y Entregas")

    if not df.empty:
        pendientes = df[df['entrega'] != 'Entregado']
        if not pendientes.empty:
            st.dataframe(pendientes[['n_pedido', 'cliente', 'producto', 'entrega', 'estado']], use_container_width=True, hide_index=True, height=420)
            st.divider()
            with st.form("form_actualizar_entrega"):
                col_x, col_y = st.columns(2)
                pedido_a_actualizar = col_x.selectbox("Seleccionar N° de Pedido:", pendientes['n_pedido'].tolist())
                nuevo_estado = col_y.selectbox("Cambiar estado a:", ["Entregado", "Envío", "Retira"])
                btn_actualizar = st.form_submit_button("Actualizar 🔄")

                if btn_actualizar:
                    actualizar_estado_entrega(pedido_a_actualizar, nuevo_estado)
                    st.success(f"¡Pedido {pedido_a_actualizar} actualizado a {nuevo_estado}!")
                    time.sleep(1)
                    st.rerun()
        else:
            st.success("¡Excelente! Todos los pedidos están entregados. 🎉")
    else:
        st.info("Aún no hay pedidos para gestionar.")

elif menu == "📲 CRM y Promociones":
    st.header("📲 Fidelización de Clientes")
    if not df.empty:
        clientes_con_telefono = df[df['telefono'].fillna('') != '']
        if not clientes_con_telefono.empty:
            cliente_elegido = st.selectbox("1. Seleccioná un cliente:", clientes_con_telefono['cliente'].unique())
            tel_cliente = clientes_con_telefono[clientes_con_telefono['cliente'] == cliente_elegido]['telefono'].iloc[0]

            st.markdown("### 2. Armá tu oferta del momento:")
            mensaje_base = f"¡Hola {cliente_elegido}! Ya tenemos disponible nuestro Catálogo Especial para el Día del Maestro en BEN AURA 🎁..."
            mensaje_personalizado = st.text_area("Podés modificar este texto:", value=mensaje_base, height=100)

            link_wsp = f"https://wa.me/{tel_cliente}?text={urllib.parse.quote(mensaje_personalizado)}"
            st.markdown(f'<br><a href="{link_wsp}" target="_blank"><button style="background-color:#25D366; color:white; padding:10px 20px; border:none; border-radius:5px; font-weight:bold; cursor:pointer;">Enviar por WhatsApp Business 🚀</button></a>', unsafe_allow_html=True)
        else:
            st.warning("Aún no tenés clientes con teléfono registrado.")
    else:
        st.info("Aún no hay clientes registrados.")

elif menu == "📢 Anuncios (Próximamente)":
    st.header("📢 Seguimiento de Pauta Publicitaria")
    st.info("Esta sección está en construcción para conectar las métricas de tus anuncios.")