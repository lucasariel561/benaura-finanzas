"""
BEN AURA — Capa de acceso a datos
Todas las funciones que tocan MySQL/TiDB viven acá.
"""

import streamlit as st
import pandas as pd
import mysql.connector
from mysql.connector import Error, pooling

DB_NAME = "benaura_db"

# ============================================================
# Conexión con Connection Pool (evita reconectar por cada query)
# ============================================================

_POOL = None

def _get_pool():
    global _POOL
    if _POOL is None:
        kwargs = {
            "pool_name": "benaura_pool",
            "pool_size": 5,
            "pool_reset_session": True,
            "host": str(st.secrets["DB_HOST"]).strip(),
            "user": str(st.secrets["DB_USER"]).strip(),
            "password": str(st.secrets["DB_PASSWORD"]).strip(),
            "port": int(st.secrets["DB_PORT"]),
            "database": DB_NAME,
        }
        # TiDB Cloud requiere SSL habilitado
        if "tidbcloud" in str(st.secrets.get("DB_HOST", "")).lower():
            kwargs["ssl_disabled"] = False
        _POOL = pooling.MySQLConnectionPool(**kwargs)
    return _POOL


def get_connection(use_db: bool = True):
    """Devuelve una conexión activa del pool. Reutiliza conexiones TCP/SSL existentes."""
    try:
        if use_db:
            return _get_pool().get_connection()
        else:
            config = {
                "host": str(st.secrets["DB_HOST"]).strip(),
                "user": str(st.secrets["DB_USER"]).strip(),
                "password": str(st.secrets["DB_PASSWORD"]).strip(),
                "port": int(st.secrets["DB_PORT"]),
            }
            if "tidbcloud" in str(st.secrets.get("DB_HOST", "")).lower():
                config["ssl_disabled"] = False
            return mysql.connector.connect(**config)
    except Error as e:
        st.error(f"❌ No se pudo conectar a la base de datos: {e}")
        st.stop()


# ============================================================
# Ventas
# ============================================================

@st.cache_data(ttl=30)
def cargar_datos() -> pd.DataFrame:
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM ventas ORDER BY fecha DESC, id DESC", conn)
    conn.close()
    return df


def insertar_venta(fecha, pedido, cliente, telefono, producto,
                   cantidad, precio_u, total, medio_pago, estado, ganancia):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO ventas
            (fecha, n_pedido, cliente, telefono, producto, cantidad,
             precio_unitario, total, medio_pago, estado, ganancia)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """, (fecha, pedido, cliente, telefono, producto,
          cantidad, precio_u, total, medio_pago, estado, ganancia))
    conn.commit()
    conn.close()
    invalidar_caches()


def actualizar_venta(id_venta, cliente, cantidad, precio_unitario,
                     medio_pago, estado, costo_unitario_original):
    total_nuevo    = cantidad * precio_unitario
    ganancia_nueva = total_nuevo - (cantidad * costo_unitario_original)
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE ventas
        SET cliente=%s, cantidad=%s, precio_unitario=%s,
            total=%s, ganancia=%s, medio_pago=%s, estado=%s
        WHERE id=%s
    """, (cliente, cantidad, precio_unitario, total_nuevo,
          ganancia_nueva, medio_pago, estado, id_venta))
    conn.commit()
    conn.close()
    invalidar_caches()


def eliminar_venta(id_venta: int):
    """Elimina una venta y restaura el stock del producto correspondiente."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT producto, cantidad FROM ventas WHERE id = %s", (id_venta,))
    venta = cursor.fetchone()
    if venta and venta["producto"]:
        prod = obtener_producto_por_nombre(venta["producto"])
        if prod:
            _restaurar_stock_conn(cursor, prod["id"], venta["cantidad"])
    cursor.execute("DELETE FROM ventas WHERE id = %s", (id_venta,))
    conn.commit()
    conn.close()
    invalidar_caches()
    cargar_productos.clear()


def actualizar_estado_pedido(id_venta: int, nuevo_estado: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE ventas SET estado=%s WHERE id=%s", (nuevo_estado, id_venta))
    conn.commit()
    conn.close()
    invalidar_caches()


def invalidar_caches():
    cargar_datos.clear()
    obtener_proximo_pedido.clear()


@st.cache_data(ttl=60)
def obtener_proximo_pedido() -> str:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COALESCE(MAX(CAST(n_pedido AS UNSIGNED)), 0) FROM ventas")
    max_pedido = cursor.fetchone()[0]
    conn.close()
    return f"{(int(max_pedido) + 1):03d}"


# ============================================================
# Productos
# ============================================================

@st.cache_data(ttl=120)
def cargar_productos() -> pd.DataFrame:
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM productos ORDER BY nombre", conn)
    conn.close()
    if not df.empty and "margen" not in df.columns:
        df["margen"] = 0.50
    return df


def guardar_producto(id_producto, nombre, stock, gramos_cera,
                     gramos_esencia, gramos_colorante, cm_pabilo,
                     precio_unitario, margen: float):
    conn = get_connection()
    cursor = conn.cursor()
    # Asegurarse de que la columna margen exista si aún no ejecutaron el ALTER TABLE manual
    try:
        cursor.execute("ALTER TABLE productos ADD COLUMN margen decimal(5,4) DEFAULT 0.5000")
        conn.commit()
    except Exception:
        pass

    try:
        if id_producto:
            cursor.execute("""
                UPDATE productos
                SET nombre=%s, stock=%s, gramos_cera=%s, gramos_esencia=%s,
                    gramos_colorante=%s, cm_pabilo=%s, precio_unitario=%s, margen=%s
                WHERE id=%s
            """, (nombre, stock, gramos_cera, gramos_esencia,
                  gramos_colorante, cm_pabilo, precio_unitario, margen, id_producto))
        else:
            cursor.execute("""
                INSERT INTO productos
                    (nombre, stock, gramos_cera, gramos_esencia,
                     gramos_colorante, cm_pabilo, precio_unitario, margen)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
            """, (nombre, stock, gramos_cera, gramos_esencia,
                  gramos_colorante, cm_pabilo, precio_unitario, margen))
    except Exception:
        # Fallback por si acaso la columna margen no se pudo agregar
        if id_producto:
            cursor.execute("""
                UPDATE productos
                SET nombre=%s, stock=%s, gramos_cera=%s, gramos_esencia=%s,
                    gramos_colorante=%s, cm_pabilo=%s, precio_unitario=%s
                WHERE id=%s
            """, (nombre, stock, gramos_cera, gramos_esencia,
                  gramos_colorante, cm_pabilo, precio_unitario, id_producto))
        else:
            cursor.execute("""
                INSERT INTO productos
                    (nombre, stock, gramos_cera, gramos_esencia,
                     gramos_colorante, cm_pabilo, precio_unitario)
                VALUES (%s,%s,%s,%s,%s,%s,%s)
            """, (nombre, stock, gramos_cera, gramos_esencia,
                  gramos_colorante, cm_pabilo, precio_unitario))
    conn.commit()
    conn.close()
    cargar_productos.clear()


def descontar_stock(id_producto: int, cantidad: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE productos SET stock = GREATEST(stock - %s, 0) WHERE id = %s",
        (cantidad, id_producto)
    )
    conn.commit()
    conn.close()
    cargar_productos.clear()


def restaurar_stock(id_producto: int, cantidad: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE productos SET stock = stock + %s WHERE id = %s",
        (cantidad, id_producto)
    )
    conn.commit()
    conn.close()
    cargar_productos.clear()


def _restaurar_stock_conn(cursor, id_producto: int, cantidad: int):
    """Restaura stock usando un cursor ya abierto (uso interno)."""
    cursor.execute(
        "UPDATE productos SET stock = stock + %s WHERE id = %s",
        (cantidad, id_producto)
    )


def obtener_producto_por_nombre(nombre: str) -> dict | None:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id FROM productos WHERE nombre = %s", (nombre,))
    fila = cursor.fetchone()
    conn.close()
    return fila


# ============================================================
# Compras de insumos
# ============================================================

@st.cache_data(ttl=60)
def cargar_compras_insumos() -> pd.DataFrame:
    conn = get_connection()
    df = pd.read_sql_query(
        "SELECT * FROM compras_insumos ORDER BY fecha DESC, id DESC", conn
    )
    conn.close()
    return df


def insertar_compra_insumo(fecha: str, insumo: str, cantidad: float, precio_total: float):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO compras_insumos (fecha, insumo, cantidad, precio_total)
        VALUES (%s, %s, %s, %s)
    """, (fecha, insumo, cantidad, precio_total))
    conn.commit()
    conn.close()
    cargar_compras_insumos.clear()


def obtener_tarifas_actuales(compras_df: pd.DataFrame) -> dict:
    """Devuelve el costo por unidad de cada insumo según la compra más reciente."""
    tarifas: dict = {}
    if not compras_df.empty:
        ultima = compras_df.sort_values(["fecha", "id"]).groupby("insumo").tail(1)
        for _, fila in ultima.iterrows():
            cantidad = float(fila["cantidad"])
            tarifas[fila["insumo"]] = {
                "costo_unitario": (float(fila["precio_total"]) / cantidad) if cantidad else 0.0,
                "fecha": fila["fecha"],
            }
    return tarifas


def costo_de(tarifas: dict, insumo: str) -> float:
    return tarifas.get(insumo, {}).get("costo_unitario", 0.0)


# ============================================================
# Config insumos
# ============================================================

def obtener_config_insumos() -> dict:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM config_insumos WHERE id = 1")
    fila = cursor.fetchone()
    conn.close()
    return fila or {"margen_objetivo": 0.5}
