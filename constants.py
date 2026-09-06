# ============================================================
# BEN AURA — Constantes globales
# ============================================================

# --- Paleta de marca ---
MARFIL  = "#F6F1EA"
CREMA   = "#EFE6D8"
ARENA   = "#DED0B8"
TAUPE   = "#A68F75"
MARRON  = "#6F5B47"
OK      = "#6F8F6A"
ALERTA  = "#C47F4B"
PELIGRO = "#B1554A"

# --- Meses en español ---
MESES_ES = {
    1: "Enero",    2: "Febrero",   3: "Marzo",     4: "Abril",
    5: "Mayo",     6: "Junio",     7: "Julio",      8: "Agosto",
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre",
}

# --- Insumos y sus unidades de medida ---
UNIDAD_INSUMO = {
    "Cera":        "gramos",
    "Esencia":     "gramos",
    "Colorante":   "gramos",
    "Pabilo":      "cm",
    "Bolsa":       "unidades",
    "Brochet":     "unidades",
    "Sticker":     "unidades",
    "Papel Madera": "unidades",
    "Cinta Bebé":  "unidades",
}
INSUMOS_MATERIALES = ["Cera", "Esencia", "Colorante", "Pabilo"]
INSUMOS_PACKAGING  = ["Bolsa", "Brochet", "Sticker", "Papel Madera", "Cinta Bebé"]

# --- Estados unificados del pedido ---
# Antes había dos campos separados (estado + entrega). Ahora uno solo.
ESTADOS_PEDIDO = [
    "⏳ Pendiente",
    "💰 Pago recibido",
    "🚚 Enviado",
    "✅ Entregado",
    "❌ Cancelado",
]

MEDIOS_PAGO = ["Transferencia", "Efectivo"]


def normalizar_estado(estado: str, entrega: str | None = None) -> str:
    """Convierte registros viejos (estado + entrega separados) al nuevo
    estado unificado. Los registros nuevos ya vienen con el valor correcto."""
    # Si el estado ya tiene el formato nuevo, lo devuelve tal cual
    for e in ESTADOS_PEDIDO:
        if estado == e:
            return estado

    # Migración de valores legacy
    if estado == "Cancelado":
        return "❌ Cancelado"
    if entrega == "Entregado":
        return "✅ Entregado"
    if entrega == "Envío":
        return "🚚 Enviado"
    if estado == "Pagado":
        return "💰 Pago recibido"
    return "⏳ Pendiente"
